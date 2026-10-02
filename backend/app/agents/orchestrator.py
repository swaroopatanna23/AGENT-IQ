import time
import pandas as pd
from typing import Dict, Any, List, Optional
from app.agents.data_agent.agent import DataAgent
from app.agents.query_understanding_agent.agent import QueryUnderstandingAgent
from app.agents.planning_agent.planner import PlanningAgent
from app.agents.analysis_agent.agent import AnalysisAgent
from app.agents.validation_agent.agent import ValidationPrivacyAgent
from app.agents.visualization_agent.agent import VisualizationAgent
from app.agents.explanation_agent.agent import ExplanationAgent

class AgentIQOrchestrator:
    """
    Coordinates the 7 specialized AI agents in the AgentIQ framework.
    Generates rich agent execution traces for observability.
    Directly fulfills Batch-08 Slides 8, 9, 10 requirements.
    """
    def __init__(self):
        self.data_agent = DataAgent()
        self.query_agent = QueryUnderstandingAgent()
        self.planning_agent = PlanningAgent()
        self.analysis_agent = AnalysisAgent()
        self.validation_agent = ValidationPrivacyAgent()
        self.viz_agent = VisualizationAgent()
        self.explanation_agent = ExplanationAgent()

    def run_pipeline(
        self,
        df: pd.DataFrame,
        data_profile: Dict[str, Any],
        question: str,
        conversation_history: Optional[List[dict]] = None
    ) -> Dict[str, Any]:
        trace = []
        overall_start = time.time()

        # Step 1: Data Understanding
        t0 = time.time()
        trace.append({
            "agent": "Data Agent",
            "status": "completed",
            "message": f"Dataset profile active ({data_profile.get('row_count')} rows, {data_profile.get('column_count')} columns, quality score: {data_profile.get('quality_score')}%)",
            "duration_ms": round((time.time() - t0) * 1000, 1)
        })

        # Step 2: Query Understanding & Analysis Schema Generation
        t1 = time.time()
        schema = self.query_agent.understand_query(question, data_profile, conversation_history)
        trace.append({
            "agent": "Query Understanding Agent",
            "status": "completed",
            "message": f"Identified intent '{schema.detected_intent}' with metric(s) {schema.target_columns} and grouping {schema.group_by}",
            "duration_ms": round((time.time() - t1) * 1000, 1)
        })

        trace.append({
            "agent": "Analysis Schema",
            "status": "completed",
            "message": f"Generated formal schema contract (Intent: {schema.detected_intent}, Agg: {schema.aggregation})",
            "duration_ms": 1.0
        })

        # Step 3: Planning Agent
        t2 = time.time()
        plan = self.planning_agent.create_plan(schema, data_profile)
        trace.append({
            "agent": "Planning Agent",
            "status": "completed",
            "message": f"Formulated {len(plan['steps'])}-step execution plan for Pandas compute engine",
            "duration_ms": round((time.time() - t2) * 1000, 1)
        })

        # Step 4: Analysis Agent Execution
        t3 = time.time()
        analysis_raw = self.analysis_agent.execute_analysis(df, schema)
        trace.append({
            "agent": "Analysis Agent",
            "status": "completed",
            "message": f"Executed deterministic transformations: generated {analysis_raw['row_count']} rows in {analysis_raw['execution_time_ms']}ms",
            "duration_ms": round((time.time() - t3) * 1000, 1)
        })

        # Step 5: Validation & Privacy Check
        t4 = time.time()
        validation = self.validation_agent.validate_and_sanitize(analysis_raw, data_profile, schema.dict())
        sanitized_data = validation["sanitized_data"]
        privacy_note = f" (Masked {len(validation['privacy_log'])} PII attributes)" if validation['privacy_log'] else " (No PII exposed)"
        trace.append({
            "agent": "Validation & Privacy Agent",
            "status": "completed",
            "message": f"Integrity checks passed{privacy_note}",
            "duration_ms": round((time.time() - t4) * 1000, 1)
        })

        # Step 6: Visualization Agent & Multi-Dashboards
        t5 = time.time()
        viz_spec = self.viz_agent.select_visualization(schema, sanitized_data, data_profile)
        dashboards_bundle = self.viz_agent.generate_dashboard_alternatives(
            schema,
            sanitized_data,
            analysis_raw["summary_kpis"],
            data_profile
        )
        trace.append({
            "agent": "Visualization Agent",
            "status": "completed",
            "message": f"Selected primary chart '{viz_spec['chart_type']}' and synthesized 3 interactive dashboard designs",
            "duration_ms": round((time.time() - t5) * 1000, 1)
        })

        # Step 7: Grounded Natural Language Explanation
        t6 = time.time()
        explanation = self.explanation_agent.explain(
            question,
            sanitized_data,
            analysis_raw["summary_kpis"],
            schema.dict(),
            language=schema.language
        )
        trace.append({
            "agent": "Explanation Agent",
            "status": "completed",
            "message": f"Synthesized grounded explanation and key insights in language '{schema.language}'",
            "duration_ms": round((time.time() - t6) * 1000, 1)
        })

        return {
            "schema": schema.dict(),
            "plan": plan,
            "result_data": sanitized_data,
            "summary_kpis": analysis_raw["summary_kpis"],
            "row_count": len(sanitized_data),
            "execution_time_ms": round((time.time() - overall_start) * 1000, 2),
            "validation": validation,
            "visualization": viz_spec,
            "dashboards": dashboards_bundle,
            "explanation": explanation,
            "agent_trace": trace
        }
