import time
import pandas as pd
from typing import Dict, Any, List
from app.schemas.analysis import AnalysisSchema
from app.agents.analysis_agent.tools import AnalysisTools

class AnalysisAgent:
    """
    Analysis Agent: Executes deterministic computations using controlled Pandas tools.
    Zero arbitrary code execution.
    Directly fulfills Batch-08 Slide 8, 9, 10 requirements.
    """

    def execute_analysis(self, df: pd.DataFrame, schema: AnalysisSchema) -> Dict[str, Any]:
        start_time = time.time()
        
        if df is None or df.empty:
            return {
                "status": "error",
                "message": "Dataset is empty",
                "result_data": [],
                "summary_kpis": {},
                "row_count": 0,
                "execution_time_ms": 0.0
            }

        # 1. Apply Filters
        working_df = AnalysisTools.filter_data(df, schema.filters)
        
        if working_df.empty:
            return {
                "status": "success",
                "message": "The filter conditions returned 0 matching records.",
                "result_data": [],
                "summary_kpis": {"Matched Records": 0},
                "row_count": 0,
                "execution_time_ms": round((time.time() - start_time) * 1000, 2)
            }

        result_df = pd.DataFrame()
        kpis = {}

        # 2. Execute Intent-Specific Workflow
        if schema.group_by and schema.target_columns:
            # Group Comparison / Aggregation
            agg_func = schema.aggregation or "avg"
            result_df = AnalysisTools.group_and_aggregate(
                working_df,
                schema.group_by,
                schema.target_columns,
                agg_func
            )
            # Sort
            sort_col = schema.sorting.column if schema.sorting else schema.target_columns[0]
            asc = schema.sorting.ascending if schema.sorting else False
            result_df = AnalysisTools.sort_data(result_df, sort_col, ascending=asc, limit=schema.limit)
            
            # Compute KPIs
            main_metric = schema.target_columns[0]
            if main_metric in working_df.columns and pd.api.types.is_numeric_dtype(working_df[main_metric]):
                kpis[f"Overall Average {main_metric}"] = round(float(working_df[main_metric].mean()), 2)
                kpis[f"Overall Total {main_metric}"] = round(float(working_df[main_metric].sum()), 2)
                if not result_df.empty:
                    top_row = result_df.iloc[0]
                    grp_val = top_row[schema.group_by[0]]
                    top_val = top_row[main_metric]
                    kpis[f"Top {schema.group_by[0]}"] = f"{grp_val} ({top_val})"

        elif schema.detected_intent == "trend_over_time" and schema.group_by and schema.target_columns:
            date_col = schema.group_by[0]
            metric_col = schema.target_columns[0]
            result_df = AnalysisTools.calculate_trend(working_df, date_col, metric_col)
            kpis["Time Periods"] = len(result_df)
            kpis[f"Total {metric_col}"] = round(float(result_df[metric_col].sum()), 2) if not result_df.empty else 0

        elif schema.detected_intent == "correlation" and len(schema.target_columns) >= 2:
            c1, c2 = schema.target_columns[0], schema.target_columns[1]
            corr_info = AnalysisTools.calculate_correlation(working_df, c1, c2)
            kpis["Correlation Coefficient"] = corr_info["correlation"]
            kpis["Relationship Strength"] = corr_info["strength"].capitalize()
            # Return sample scatter points
            sample_df = working_df[[c1, c2]].dropna().head(100)
            result_df = sample_df

        elif schema.target_columns and not schema.group_by:
            # Single or multi-metric overall statistics
            main_col = schema.target_columns[0]
            stats = AnalysisTools.calculate_statistics(working_df, main_col)
            kpis = {f"{k.capitalize()} {main_col}": v for k, v in stats.items()}
            # Convert stats to a 1-row table
            result_df = pd.DataFrame([stats])

        else:
            # General overview / fallback
            if schema.group_by:
                result_df = working_df[schema.group_by[0]].value_counts().head(10).reset_index()
                result_df.columns = [schema.group_by[0], "Count"]
            else:
                result_df = working_df.head(20)
            kpis["Total Records"] = len(working_df)

        elapsed = round((time.time() - start_time) * 1000, 2)
        records = result_df.to_dict(orient="records") if not result_df.empty else []

        return {
            "status": "success",
            "result_data": records,
            "summary_kpis": kpis,
            "row_count": len(records),
            "execution_time_ms": elapsed
        }
