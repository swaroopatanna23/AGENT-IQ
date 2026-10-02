from typing import Dict, Any, List, Optional
from app.schemas.analysis import AnalysisSchema

class VisualizationAgent:
    """
    Visualization Agent: Automatically selects suitable chart types
    and generates multiple dashboard alternatives.
    Directly fulfills Batch-08 Slide 8, 9, 12 requirements.
    """

    def select_visualization(
        self,
        schema: AnalysisSchema,
        result_data: List[Dict[str, Any]],
        data_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determines the primary recommended chart and alternative options.
        """
        if not result_data:
            return {"primary_chart": "table", "alternatives": []}

        sample_row = result_data[0]
        keys = list(sample_row.keys())

        # Intent-driven & data-shape-driven rules
        if schema.requested_visualization:
            primary = schema.requested_visualization
            return self._build_spec(primary, schema, keys, result_data)

        # 1. Two numerical dimensions -> Scatter Plot
        if schema.detected_intent == "correlation" and len(schema.target_columns) >= 2:
            return self._build_spec("scatter", schema, keys, result_data)

        # 2. Time dimension + Metric -> Line or Area Chart
        date_cols = data_profile.get("datetime_columns", [])
        if any(g in date_cols for g in schema.group_by) or schema.detected_intent == "trend_over_time":
            return self._build_spec("line", schema, keys, result_data)

        # 3. Categorical + 1 Metric
        if schema.group_by and schema.target_columns:
            n_categories = len(result_data)
            if schema.detected_intent == "ranking" or n_categories > 7:
                return self._build_spec("horizontal_bar", schema, keys, result_data)
            elif n_categories <= 5 and schema.aggregation in ["sum", "count"]:
                return self._build_spec("donut", schema, keys, result_data)
            else:
                return self._build_spec("bar", schema, keys, result_data)

        # 4. Single Metric Summary -> KPI Card
        if schema.target_columns and not schema.group_by:
            return self._build_spec("kpi_card", schema, keys, result_data)

        # Fallback: Bar or Table
        if len(keys) >= 2:
            return self._build_spec("bar", schema, keys, result_data)
        return self._build_spec("table", schema, keys, result_data)

    def _build_spec(self, chart_type: str, schema: AnalysisSchema, keys: List[str], data: List[dict]) -> Dict[str, Any]:
        x_col = schema.group_by[0] if schema.group_by and schema.group_by[0] in keys else (keys[0] if keys else "")
        y_col = schema.target_columns[0] if schema.target_columns and schema.target_columns[0] in keys else (keys[1] if len(keys) > 1 else x_col)

        alternatives = ["bar", "horizontal_bar", "line", "pie", "donut", "table"]
        if chart_type in alternatives:
            alternatives.remove(chart_type)

        return {
            "chart_type": chart_type,
            "x_axis": x_col,
            "y_axis": y_col,
            "title": f"{schema.aggregation.capitalize() if schema.aggregation else 'Analysis'} of {y_col} by {x_col}" if x_col != y_col else f"{y_col} Overview",
            "alternatives": alternatives[:3],
            "data": data
        }

    def generate_dashboard_alternatives(
        self,
        schema: AnalysisSchema,
        result_data: List[Dict[str, Any]],
        kpis: Dict[str, Any],
        data_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generates 3 distinct dashboard design alternatives (Designs A, B, and C)
        matching Batch-08 Slide 8, 9 ('Multiple Dashboards').
        """
        spec = self.select_visualization(schema, result_data, data_profile)
        x_axis = spec.get("x_axis", "")
        y_axis = spec.get("y_axis", "")

        # Design A: Executive Summary
        design_a = {
            "id": "design_a",
            "name": "Design A: Executive Summary",
            "description": "High-level overview featuring key performance indicators and primary aggregation chart.",
            "components": [
                {"id": "c1", "type": "kpi_card", "title": "Key Metrics", "data": kpis, "position": {"w": 12, "h": 2}},
                {"id": "c2", "type": spec["chart_type"], "title": spec["title"], "config": spec, "data": result_data, "position": {"w": 8, "h": 4}},
                {"id": "c3", "type": "donut", "title": f"Distribution by {x_axis}", "config": {"x_axis": x_axis, "y_axis": y_axis}, "data": result_data[:6], "position": {"w": 4, "h": 4}}
            ]
        }

        # Design B: Detailed Breakdown
        design_b = {
            "id": "design_b",
            "name": "Design B: Detailed Breakdown",
            "description": "Granular comparison with sorted bar breakdown, category shares, and tabular audit log.",
            "components": [
                {"id": "c4", "type": "horizontal_bar", "title": f"Ranked {y_axis} by {x_axis}", "config": {"x_axis": x_axis, "y_axis": y_axis}, "data": result_data, "position": {"w": 6, "h": 4}},
                {"id": "c5", "type": "pie", "title": "Category Proportions", "config": {"x_axis": x_axis, "y_axis": y_axis}, "data": result_data[:8], "position": {"w": 6, "h": 4}},
                {"id": "c6", "type": "table", "title": "Detailed Data Records", "data": result_data, "position": {"w": 12, "h": 4}}
            ]
        }

        # Design C: Trend & Comparison
        design_c = {
            "id": "design_c",
            "name": "Design C: Trend & Comparison",
            "description": "Multi-angle visual perspective showcasing trend continuity, comparative bars, and outlier signals.",
            "components": [
                {"id": "c7", "type": "line", "title": f"Trend Trajectory of {y_axis}", "config": {"x_axis": x_axis, "y_axis": y_axis}, "data": result_data, "position": {"w": 8, "h": 4}},
                {"id": "c8", "type": "kpi_card", "title": "Highlights", "data": kpis, "position": {"w": 4, "h": 4}},
                {"id": "c9", "type": "bar", "title": f"Variance Comparison", "config": {"x_axis": x_axis, "y_axis": y_axis}, "data": result_data, "position": {"w": 12, "h": 4}}
            ]
        }

        return {
            "active_design": "design_a",
            "designs": [design_a, design_b, design_c]
        }
