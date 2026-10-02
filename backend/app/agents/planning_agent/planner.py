from typing import Dict, Any, List
from app.schemas.analysis import AnalysisSchema

class PlanningAgent:
    """
    Planning Agent: Formulates an explicit, verifiable, deterministic execution plan
    from the AnalysisSchema and DataProfile.
    Directly fulfills Batch-08 Slide 8, 9 requirements.
    """

    def create_plan(self, schema: AnalysisSchema, data_profile: Dict[str, Any]) -> Dict[str, Any]:
        steps: List[str] = []
        
        # Step 1: Verification
        target_str = ", ".join(f"'{c}'" for c in schema.target_columns) if schema.target_columns else "all records"
        group_str = ", ".join(f"'{c}'" for c in schema.group_by) if schema.group_by else "None"
        steps.append(f"Verify dataset columns: Target metrics: [{target_str}], Group dimensions: [{group_str}]")

        # Step 2: Filtering
        if schema.filters:
            filter_descs = [f"'{f.column}' {f.operator} {f.value}" for f in schema.filters]
            steps.append(f"Apply data filters: {', '.join(filter_descs)}")
        else:
            steps.append("Load entire dataset partition (No row-level filters specified)")

        # Step 3: Aggregation / Transformation
        if schema.group_by and schema.target_columns:
            agg_type = (schema.aggregation or "average").upper()
            steps.append(f"Group records by [{group_str}] and compute {agg_type} of [{target_str}]")
        elif schema.target_columns and not schema.group_by:
            agg_type = (schema.aggregation or "sum").upper()
            steps.append(f"Calculate overall dataset aggregate: {agg_type} of [{target_str}]")
        elif schema.detected_intent == "correlation":
            steps.append(f"Compute Pearson correlation coefficient between selected metrics")
        elif schema.detected_intent == "distribution":
            steps.append(f"Calculate numerical histogram bin frequencies and descriptive statistics")
        else:
            steps.append(f"Compute summary metrics and category distributions")

        # Step 4: Sorting & Ranking
        if schema.sorting:
            dir_str = "descending" if not schema.sorting.ascending else "ascending"
            steps.append(f"Sort transformed results by '{schema.sorting.column}' in {dir_str} order")
            if schema.limit:
                steps.append(f"Limit output to top {schema.limit} entries")
        elif schema.group_by:
            steps.append("Sort results by metric descending for clear comparative presentation")

        # Step 5: Privacy & Validation Checks
        steps.append("Pass calculated results through Validation and Privacy Agent (PII scan & sanity check)")

        # Step 6: Visualization Selection
        steps.append("Select optimal chart representation and multi-dashboard layout alternatives")

        # Step 7: Natural Language Explanation
        steps.append("Generate grounded natural-language findings and business takeaways")

        return {
            "steps": steps,
            "compute_engine": "pandas",
            "intent": schema.detected_intent
        }
