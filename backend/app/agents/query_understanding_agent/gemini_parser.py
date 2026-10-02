import json
import os
import re
from typing import Dict, Any, List, Optional
from app.config import settings

class GeminiQueryParser:
    """
    Multilingual Semantic Query Parser powered by Google GenAI.
    Directly extracts structured AnalysisSchema slot values.
    """
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Could not initialize Google GenAI Client: {e}")

    def parse(self, question: str, columns_meta: List[Dict[str, Any]], conversation_history: Optional[List[dict]] = None) -> Optional[Dict[str, Any]]:
        if not self.client:
            return None

        col_names = [c["name"] for c in columns_meta]
        num_cols = [c["name"] for c in columns_meta if c.get("type") == "numerical"]
        cat_cols = [c["name"] for c in columns_meta if c.get("type") in ["categorical", "text"]]
        date_cols = [c["name"] for c in columns_meta if c.get("type") == "datetime"]

        system_instruction = f"""
You are the Query Understanding Agent for AgentIQ.
Your task is to analyze the user's natural language question and extract a strictly valid AnalysisSchema JSON.

ACTUAL DATASET COLUMNS AVAILABLE:
- All Columns: {col_names}
- Numerical Columns: {num_cols}
- Categorical Columns: {cat_cols}
- Date/Time Columns: {date_cols}

RULES:
1. STRICTLY map target_columns and group_by to the EXACT column names listed above. Never invent new column names.
2. The user might query in English, Hindi, Telugu, Spanish, French, etc. Translate the intent to standard schema parameters while detecting language.
3. If user asks "What is average marks by age?", target_columns=['marks'], group_by=['age'], aggregation='avg', intent='group_comparison'.
4. If user asks "Which region has the highest sales?", target_columns=['sales' or corresponding sales col], group_by=['region'], aggregation='sum', intent='ranking', sorting={'column': 'sales', 'ascending': false}, limit=1.
5. If follow-up context is given, incorporate it.

Return ONLY a valid JSON object with the following schema:
{{
  "detected_intent": "aggregation" | "group_comparison" | "trend_over_time" | "distribution" | "correlation" | "ranking" | "outlier_detection" | "overview",
  "target_columns": ["col_name"],
  "group_by": ["col_name"],
  "filters": [
    {{"column": "col_name", "operator": "eq"|"neq"|"gt"|"gte"|"lt"|"lte"|"in", "value": "val"}}
  ],
  "aggregation": "avg" | "sum" | "count" | "min" | "max" | "median" | null,
  "sorting": {{"column": "col_name", "ascending": true|false}} | null,
  "limit": number | null,
  "time_granularity": "day" | "month" | "year" | null,
  "requested_visualization": "bar" | "line" | "pie" | "scatter" | "histogram" | "heatmap" | "kpi_card" | null,
  "language": "en" | "hi" | "te" | "es" | "fr" | etc.
}}
"""
        context_str = ""
        if conversation_history:
            context_str = f"PREVIOUS CONVERSATION CONTEXT:\n{json.dumps(conversation_history[-3:])}\n\n"

        prompt = f"{context_str}USER QUESTION: {question}"

        try:
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config={
                    "system_instruction": system_instruction,
                    "response_mime_type": "application/json"
                }
            )
            raw_text = response.text.strip()
            # Clean markdown codeblocks if returned
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
                raw_text = re.sub(r"\s*```$", "", raw_text)
            parsed = json.loads(raw_text)
            return parsed
        except Exception as e:
            print(f"Gemini API parse error: {e}")
            return None
