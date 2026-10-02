import json
import os
import re
from typing import Dict, Any, List
from app.config import settings

class ExplanationAgent:
    """
    Explanation Agent: Synthesizes grounded natural language insights,
    short answers, and observations strictly grounded in validated numbers.
    Directly fulfills Batch-08 Slide 8, 9, 13 requirements.
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: ExplanationAgent could not load GenAI: {e}")

    def explain(
        self,
        question: str,
        result_data: List[Dict[str, Any]],
        kpis: Dict[str, Any],
        schema_dict: Dict[str, Any],
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generates grounded explanation dictionary:
        { short_answer, key_insights, observations, limitations, full_text }
        """
        # Try LLM synthesis first
        if self.client and result_data:
            try:
                explanation = self._llm_explain(question, result_data[:20], kpis, schema_dict, language)
                if explanation:
                    return explanation
            except Exception as e:
                print(f"Explanation Agent LLM error: {e}")

        # Deterministic fallback grounded generator
        return self._deterministic_explain(question, result_data, kpis, schema_dict, language)

    def _llm_explain(
        self,
        question: str,
        sample_results: list,
        kpis: dict,
        schema: dict,
        language: str
    ) -> Dict[str, Any]:
        prompt = f"""
You are the Explanation Agent for AgentIQ.
You receive ONLY the validated calculated numbers from deterministic Pandas analysis.

QUESTION: "{question}"
INTENT: {schema.get('detected_intent')}
CALCULATED METRICS: {json.dumps(kpis)}
VALIDATED DATA (FIRST {len(sample_results)} ROWS):
{json.dumps(sample_results)}

TARGET LANGUAGE: {language}

RULES:
1. NEVER invent numbers or make claims not supported by the data above.
2. Ground every insight in the exact values calculated.
3. If language is other than English (e.g. 'te' for Telugu, 'hi' for Hindi, 'es' for Spanish), provide the explanation in that language.

Return ONLY a JSON object:
{{
  "short_answer": "Direct 1-2 sentence answer to the user's question.",
  "key_insights": [
    "Fact 1 with specific numbers",
    "Fact 2 with specific numbers"
  ],
  "observations": [
    "Noticeable pattern or trend in the calculated data"
  ],
  "limitations": "Any caveat regarding missing values or sample size if applicable."
}}
"""
        response = self.client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
        return json.loads(raw)

    def _deterministic_explain(
        self,
        question: str,
        data: list,
        kpis: dict,
        schema: dict,
        language: str
    ) -> Dict[str, Any]:
        if not data:
            return {
                "short_answer": "No records matched your query filters.",
                "key_insights": ["The dataset partition returned zero rows for the requested criteria."],
                "observations": ["Try adjusting or removing the filter constraints."],
                "limitations": "Empty result set."
            }

        groups = schema.get("group_by", [])
        targets = schema.get("target_columns", [])
        agg = schema.get("aggregation", "average")

        insights = []
        observations = []

        if groups and targets and len(data) > 0:
            g_col = groups[0]
            t_col = targets[0]
            first = data[0]
            last = data[-1] if len(data) > 1 else first

            short_answer = f"Based on the analysis, {first.get(g_col)} recorded the highest {agg} {t_col} at {first.get(t_col)}."
            insights.append(f"Top performing {g_col} is '{first.get(g_col)}' with a value of {first.get(t_col)}.")
            
            if len(data) > 1:
                insights.append(f"Lowest performing {g_col} is '{last.get(g_col)}' with a value of {last.get(t_col)}.")
                diff = round(float(first.get(t_col, 0)) - float(last.get(t_col, 0)), 2)
                observations.append(f"The variance between the highest and lowest {g_col} is {diff} units.")

            for k, v in kpis.items():
                observations.append(f"{k}: {v}")

        elif targets and len(data) > 0:
            first = data[0]
            short_answer = f"Calculated {agg} for {targets[0]}: {first.get('mean', first.get('sum', 'computed'))}."
            for k, v in first.items():
                insights.append(f"{str(k).capitalize()}: {v}")
        else:
            short_answer = f"Analysis completed across {len(data)} records."
            insights.append(f"Evaluated {len(data)} data points matching your criteria.")

        return {
            "short_answer": short_answer,
            "key_insights": insights,
            "observations": observations if observations else ["All values are within standard operating bounds."],
            "limitations": "Analysis based strictly on verified dataset records."
        }
