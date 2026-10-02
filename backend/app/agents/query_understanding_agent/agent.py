import re
from typing import Dict, Any, List, Optional
from difflib import get_close_matches
from app.schemas.analysis import AnalysisSchema, FilterCondition, SortCondition
from app.agents.query_understanding_agent.baseline_svm import BaselineIntentClassifier
from app.agents.query_understanding_agent.gemini_parser import GeminiQueryParser

class QueryUnderstandingAgent:
    """
    Query Understanding Agent: Converts multilingual natural-language queries
    into structured, validated AnalysisSchema objects.
    Directly fulfills Batch-08 Slide 8, 9 requirements.
    """
    def __init__(self):
        self.baseline_svm = BaselineIntentClassifier()
        self.gemini_parser = GeminiQueryParser()

    def understand_query(
        self,
        question: str,
        data_profile: Dict[str, Any],
        conversation_history: Optional[List[dict]] = None
    ) -> AnalysisSchema:
        columns_meta = data_profile.get("columns", [])
        col_names = [c["name"] for c in columns_meta]

        # 1. Try Gemini parser first
        parsed = self.gemini_parser.parse(question, columns_meta, conversation_history)
        
        # 2. If Gemini unavailable or offline, use deterministic baseline + rule extraction
        if not parsed:
            parsed = self._deterministic_extract(question, data_profile, conversation_history)

        # 3. Strictly validate & normalize target_columns and group_by against real columns
        target_cols = self._match_valid_columns(parsed.get("target_columns", []), col_names)
        group_by_cols = self._match_valid_columns(parsed.get("group_by", []), col_names)
        
        # If user did not specify target but did group_by, pick best numerical column
        num_cols = data_profile.get("numerical_columns", [])
        if not target_cols and num_cols:
            valid_metrics = [c for c in num_cols if not c.lower().endswith(('_id', 'id', 'year')) and c not in group_by_cols]
            target_cols = [valid_metrics[0]] if valid_metrics else [num_cols[0]]

        # Build clean Pydantic schema
        sorting_data = parsed.get("sorting")
        sort_obj = None
        if isinstance(sorting_data, dict) and sorting_data.get("column"):
            matched_col = self._match_valid_columns([sorting_data["column"]], col_names)
            if matched_col:
                sort_obj = SortCondition(column=matched_col[0], ascending=sorting_data.get("ascending", True))

        filters_list = []
        for f in parsed.get("filters", []):
            if isinstance(f, dict) and f.get("column"):
                matched_col = self._match_valid_columns([f["column"]], col_names)
                if matched_col:
                    filters_list.append(FilterCondition(
                        column=matched_col[0],
                        operator=f.get("operator", "eq"),
                        value=f.get("value")
                    ))

        return AnalysisSchema(
            user_question=question,
            detected_intent=parsed.get("detected_intent", "group_comparison"),
            target_columns=target_cols,
            group_by=group_by_cols,
            filters=filters_list,
            aggregation=parsed.get("aggregation") or ("avg" if group_by_cols else "sum"),
            sorting=sort_obj,
            limit=parsed.get("limit"),
            time_granularity=parsed.get("time_granularity"),
            requested_visualization=parsed.get("requested_visualization"),
            language=parsed.get("language", "en")
        )

    def _deterministic_extract(self, question: str, data_profile: Dict[str, Any], context: Optional[List[dict]] = None) -> Dict[str, Any]:
        q_lower = question.lower()
        col_names = [c["name"] for c in data_profile.get("columns", [])]
        num_cols = data_profile.get("numerical_columns", [])
        cat_cols = data_profile.get("categorical_columns", [])
        date_cols = data_profile.get("datetime_columns", [])

        # Predict intent using baseline SVM
        intent = self.baseline_svm.predict_intent(question)
        
        # Detect aggregations
        agg = "avg"
        if any(w in q_lower for w in ["total", "sum", "overall"]):
            agg = "sum"
        elif any(w in q_lower for w in ["count", "how many", "number of"]):
            agg = "count"
        elif any(w in q_lower for w in ["max", "highest", "peak", "maximum"]):
            agg = "max"
        elif any(w in q_lower for w in ["min", "lowest", "minimum"]):
            agg = "min"
        elif any(w in q_lower for w in ["average", "mean", "avg"]):
            agg = "avg"

        # Explicit "by <col>" / "per <col>" / "across <col>" grouping detection
        by_col = None
        by_pattern = re.search(r"\b(?:by|per|across|for each|group by)\s+([a-zA-Z0-9_]+)", q_lower)
        if by_pattern:
            candidate = by_pattern.group(1).strip()
            matched_by = self._match_valid_columns([candidate], col_names)
            if matched_by:
                by_col = matched_by[0]

        matched_targets = []
        matched_groups = [by_col] if by_col else []

        for col in col_names:
            if col == by_col:
                continue
            c_norm = col.lower().replace("_", " ")
            if c_norm in q_lower or col.lower() in q_lower:
                if col in num_cols:
                    matched_targets.append(col)
                elif col in cat_cols or col in date_cols:
                    if col not in matched_groups:
                        matched_groups.append(col)

        # Context continuation if follow-up
        if not matched_groups and context:
            for msg in reversed(context):
                if msg.get("schema") and msg["schema"].get("group_by"):
                    matched_groups = msg["schema"]["group_by"]
                    break

        sorting = None
        limit = None
        if "highest" in q_lower or "top" in q_lower:
            target_sort = matched_targets[0] if matched_targets else (num_cols[0] if num_cols else None)
            if target_sort:
                sorting = {"column": target_sort, "ascending": False}
            top_m = re.search(r"top\s*(\d+)", q_lower)
            if top_m:
                limit = int(top_m.group(1))
            elif "highest" in q_lower:
                limit = 1 if "which" in q_lower else 5
        elif "lowest" in q_lower or "bottom" in q_lower:
            target_sort = matched_targets[0] if matched_targets else (num_cols[0] if num_cols else None)
            if target_sort:
                sorting = {"column": target_sort, "ascending": True}
            limit = 1 if "which" in q_lower else 5

        # Filters
        filters = []
        num_filter_match = re.search(r"(above|greater than|>|over)\s*(\d+(\.\d+)?)", q_lower)
        if num_filter_match:
            val = float(num_filter_match.group(2))
            col = matched_targets[0] if matched_targets else (num_cols[0] if num_cols else None)
            if col:
                filters.append({"column": col, "operator": "gt", "value": val})

        return {
            "detected_intent": intent if by_col or matched_groups else ("aggregation" if not matched_groups else intent),
            "target_columns": matched_targets,
            "group_by": matched_groups,
            "filters": filters,
            "aggregation": agg,
            "sorting": sorting,
            "limit": limit,
            "language": "en"
        }

    def _match_valid_columns(self, requested_cols: List[str], actual_cols: List[str]) -> List[str]:
        valid = []
        actual_lower = {c.lower(): c for c in actual_cols}
        for req in requested_cols:
            if not req:
                continue
            r_clean = str(req).strip()
            if r_clean in actual_cols:
                valid.append(r_clean)
            elif r_clean.lower() in actual_lower:
                valid.append(actual_lower[r_clean.lower()])
            else:
                matches = get_close_matches(r_clean.lower(), actual_lower.keys(), n=1, cutoff=0.7)
                if matches:
                    valid.append(actual_lower[matches[0]])
        return list(dict.fromkeys(valid))
