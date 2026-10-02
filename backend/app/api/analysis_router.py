import os
import pandas as pd
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.users import User
from app.models.datasets import Dataset
from app.models.queries import QueryModel, AnalysisSchemaModel, AnalysisPlanModel, AnalysisResultModel
from app.models.conversations import ConversationModel, ConversationMessageModel
from app.auth.dependencies import get_current_user
from app.data_sources.service import DataInputService
from app.agents.data_agent.agent import DataAgent
from app.agents.orchestrator import AgentIQOrchestrator

router = APIRouter(prefix="/api/v1/analysis", tags=["AI Analysis Engine"])

class QueryRequest(BaseModel):
    dataset_id: int
    question: str
    conversation_id: Optional[int] = None
    language: Optional[str] = "en"

@router.post("/query")
def execute_query(
    req: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dataset = db.query(Dataset).filter(Dataset.id == req.dataset_id, Dataset.user_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="Dataset file missing on server")

    # Load dataset
    df = DataInputService.load_data(dataset.file_format, dataset.file_path)

    # Get or compute profile
    if dataset.profile:
        data_profile = {
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "columns": dataset.profile.columns,
            "numerical_columns": dataset.profile.numerical_columns,
            "categorical_columns": dataset.profile.categorical_columns,
            "datetime_columns": dataset.profile.datetime_columns,
            "text_columns": dataset.profile.text_columns,
            "quality_score": dataset.profile.quality_score,
            "sensitive_columns": dataset.profile.sensitive_columns
        }
    else:
        data_profile = DataAgent().profile(df)

    # Manage Conversation Context
    conversation = None
    history_messages = []
    if req.conversation_id:
        conversation = db.query(ConversationModel).filter(
            ConversationModel.id == req.conversation_id,
            ConversationModel.user_id == current_user.id
        ).first()
        if conversation:
            history_messages = [
                {"sender": m.sender, "content": m.content}
                for m in conversation.messages[-6:]
            ]

    if not conversation:
        conversation = ConversationModel(
            user_id=current_user.id,
            dataset_id=dataset.id,
            title=f"Analysis of {dataset.name}"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Run Multi-Agent Orchestrator
    orchestrator = AgentIQOrchestrator()
    output = orchestrator.run_pipeline(
        df=df,
        data_profile=data_profile,
        question=req.question,
        conversation_history=history_messages
    )

    # Persist in DB
    query_record = QueryModel(
        user_id=current_user.id,
        dataset_id=dataset.id,
        conversation_id=conversation.id,
        user_question=req.question,
        detected_language=output["schema"].get("language", "en")
    )
    db.add(query_record)
    db.commit()
    db.refresh(query_record)

    # Add conversation messages
    user_msg = ConversationMessageModel(
        conversation_id=conversation.id,
        sender="user",
        content=req.question,
        language=output["schema"].get("language", "en"),
        query_id=query_record.id
    )
    agent_msg = ConversationMessageModel(
        conversation_id=conversation.id,
        sender="agent",
        content=output["explanation"]["short_answer"],
        language=output["schema"].get("language", "en"),
        query_id=query_record.id
    )
    db.add(user_msg)
    db.add(agent_msg)

    # Persist Schema
    schema_record = AnalysisSchemaModel(
        query_id=query_record.id,
        intent=output["schema"].get("detected_intent", "group_comparison"),
        target_columns=output["schema"].get("target_columns", []),
        group_by=output["schema"].get("group_by", []),
        filters=output["schema"].get("filters", []),
        aggregation=output["schema"].get("aggregation"),
        sorting=output["schema"].get("sorting"),
        limit=output["schema"].get("limit"),
        time_granularity=output["schema"].get("time_granularity"),
        requested_visualization=output["schema"].get("requested_visualization")
    )
    db.add(schema_record)

    # Persist Plan
    plan_record = AnalysisPlanModel(
        query_id=query_record.id,
        steps=output["plan"].get("steps", []),
        compute_engine=output["plan"].get("compute_engine", "pandas")
    )
    db.add(plan_record)

    # Persist Result
    result_record = AnalysisResultModel(
        query_id=query_record.id,
        execution_status="success",
        result_data=output["result_data"],
        summary_kpis=output["summary_kpis"],
        row_count=output["row_count"],
        execution_time_ms=output["execution_time_ms"],
        validation_status=output["validation"],
        visualization_spec=output["visualization"],
        explanation=output["explanation"],
        agent_trace=output["agent_trace"]
    )
    db.add(result_record)
    db.commit()

    return {
        "query_id": query_record.id,
        "conversation_id": conversation.id,
        "schema": output["schema"],
        "plan": output["plan"],
        "result_data": output["result_data"],
        "summary_kpis": output["summary_kpis"],
        "row_count": output["row_count"],
        "execution_time_ms": output["execution_time_ms"],
        "validation": output["validation"],
        "visualization": output["visualization"],
        "dashboards": output["dashboards"],
        "explanation": output["explanation"],
        "agent_trace": output["agent_trace"],
        "trace": output["agent_trace"]
    }

@router.get("/suggested-questions/{dataset_id}")
def get_suggested_questions(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.user_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    p = dataset.profile
    num_cols = p.numerical_columns if p else []
    cat_cols = p.categorical_columns if p else []
    date_cols = p.datetime_columns if p else []

    questions = ["Give me an overall summary of this dataset."]
    
    if cat_cols and num_cols:
        c = cat_cols[0]
        n = [col for col in num_cols if not col.endswith('_id')][0] if num_cols else "value"
        questions.append(f"What is average {n} by {c}?")
        questions.append(f"Which {c} has the highest {n}?")

    if date_cols and num_cols:
        d = date_cols[0]
        n = [col for col in num_cols if not col.endswith('_id')][0] if num_cols else "value"
        questions.append(f"Show the trend of {n} over time.")

    if len(num_cols) >= 2:
        clean_nums = [col for col in num_cols if not col.endswith('_id')]
        if len(clean_nums) >= 2:
            questions.append(f"What is the correlation between {clean_nums[0]} and {clean_nums[1]}?")

    if num_cols:
        n = [col for col in num_cols if not col.endswith('_id')][0]
        questions.append(f"Show the distribution of {n}.")

    questions.append("Are there any missing values or data anomalies?")
    return questions[:6]

@router.get("/history")
def get_query_history(
    dataset_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(QueryModel).filter(QueryModel.user_id == current_user.id)
    if dataset_id:
        q = q.filter(QueryModel.dataset_id == dataset_id)
    queries = q.order_by(QueryModel.created_at.desc()).limit(30).all()

    history = []
    for q_item in queries:
        res = q_item.result
        history.append({
            "id": q_item.id,
            "dataset_id": q_item.dataset_id,
            "dataset_name": q_item.dataset.name if q_item.dataset else "Dataset",
            "question": q_item.user_question,
            "intent": q_item.schema.intent if q_item.schema else "query",
            "created_at": q_item.created_at,
            "short_answer": res.explanation.get("short_answer") if res and res.explanation else "",
            "chart_type": res.visualization_spec.get("chart_type") if res and res.visualization_spec else "bar",
            "execution_time_ms": res.execution_time_ms if res else 0.0
        })
    return history
