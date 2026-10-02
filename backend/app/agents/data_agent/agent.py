import re
import numpy as np
import pandas as pd
from typing import Dict, Any, List

class DataAgent:
    """
    Data Agent: Responsible for deterministic schema detection, data-type inference,
    statistical profiling, quality scoring, and PII detection.
    Directly fulfills Batch-08 Slide 8, 9, 10 requirements.
    """

    def __init__(self):
        # Patterns for identifying sensitive / PII fields
        self.sensitive_patterns = [
            (r"(email|mail)", "Email Address", "HIGH"),
            (r"(phone|mobile|contact|tel)", "Phone Number", "HIGH"),
            (r"(ssn|social_security|national_id|aadhaar|pan)", "Government Identification", "CRITICAL"),
            (r"(credit_card|card_number|cvv|account_number)", "Financial Account", "CRITICAL"),
            (r"(patient_id|medical|diagnosis|health)", "Protected Health Information", "HIGH"),
            (r"(salary|wage|compensation)", "Confidential Financial Data", "MEDIUM"),
            (r"(password|secret|token|hash)", "Security Credential", "CRITICAL"),
        ]

    def profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Executes complete deterministic profiling on a pandas DataFrame.
        Returns a rich structured profile dictionary.
        """
        if df is None or df.empty:
            return {
                "row_count": 0,
                "column_count": 0,
                "columns": [],
                "numerical_columns": [],
                "categorical_columns": [],
                "datetime_columns": [],
                "text_columns": [],
                "missing_values": {},
                "duplicate_rows": 0,
                "quality_score": 0.0,
                "sensitive_columns": [],
                "summary_statistics": {},
                "sample_preview": []
            }

        row_count = int(len(df))
        column_count = int(len(df.columns))

        columns_meta = []
        numerical_cols = []
        categorical_cols = []
        datetime_cols = []
        text_cols = []
        missing_values_map = {}
        sensitive_columns = []
        summary_stats = {}

        # 1. Column-by-column inspection
        for col in df.columns:
            series = df[col]
            null_count = int(series.isna().sum())
            null_pct = round((null_count / max(row_count, 1)) * 100, 2)
            unique_count = int(series.nunique(dropna=True))
            
            # Sample non-null values
            sample_vals = [
                val if not pd.isna(val) else None 
                for val in series.dropna().head(4).tolist()
            ]
            # Convert non-serializable types in samples
            sample_vals = [
                str(v) if isinstance(v, (pd.Timestamp, np.datetime64)) else v
                for v in sample_vals
            ]

            # Inferred Type
            inferred_type = self._infer_column_type(series)
            if inferred_type == "numerical":
                numerical_cols.append(col)
                # Compute descriptive stats
                clean_s = series.dropna()
                if len(clean_s) > 0:
                    summary_stats[col] = {
                        "min": float(clean_s.min()),
                        "max": float(clean_s.max()),
                        "mean": round(float(clean_s.mean()), 2),
                        "std": round(float(clean_s.std()), 2) if len(clean_s) > 1 else 0.0,
                        "median": round(float(clean_s.median()), 2),
                        "q25": round(float(clean_s.quantile(0.25)), 2),
                        "q75": round(float(clean_s.quantile(0.75)), 2),
                        "outlier_count": self._detect_outliers_count(clean_s)
                    }
            elif inferred_type == "datetime":
                datetime_cols.append(col)
            elif inferred_type == "categorical":
                categorical_cols.append(col)
                # Top frequencies
                val_counts = series.value_counts(dropna=True).head(5).to_dict()
                summary_stats[col] = {
                    "top_values": {str(k): int(v) for k, v in val_counts.items()}
                }
            else:
                text_cols.append(col)

            # Check PII / Sensitivity
            pii_check = self._check_sensitive_column(col, series)
            if pii_check:
                sensitive_columns.append(pii_check)

            columns_meta.append({
                "name": str(col),
                "type": inferred_type,
                "raw_dtype": str(series.dtype),
                "null_count": null_count,
                "null_percentage": null_pct,
                "unique_count": unique_count,
                "is_sensitive": bool(pii_check),
                "sample_values": sample_vals
            })

            missing_values_map[str(col)] = {
                "count": null_count,
                "percentage": null_pct
            }

        # 2. Duplicate rows
        duplicate_rows = int(df.duplicated().sum())

        # 3. Overall Data Quality Score (0 - 100)
        quality_score = self._compute_quality_score(row_count, column_count, missing_values_map, duplicate_rows)

        # 4. Preview (first 10 records)
        preview_records = []
        for record in df.head(10).to_dict(orient="records"):
            clean_rec = {}
            for k, v in record.items():
                if pd.isna(v):
                    clean_rec[k] = None
                elif isinstance(v, (pd.Timestamp, np.datetime64)):
                    clean_rec[k] = str(v)
                elif isinstance(v, (np.integer, np.int64)):
                    clean_rec[k] = int(v)
                elif isinstance(v, (np.floating, np.float64)):
                    clean_rec[k] = round(float(v), 2)
                else:
                    clean_rec[k] = v
            preview_records.append(clean_rec)

        return {
            "row_count": row_count,
            "column_count": column_count,
            "columns": columns_meta,
            "numerical_columns": numerical_cols,
            "categorical_columns": categorical_cols,
            "datetime_columns": datetime_cols,
            "text_columns": text_cols,
            "missing_values": missing_values_map,
            "duplicate_rows": duplicate_rows,
            "quality_score": quality_score,
            "sensitive_columns": sensitive_columns,
            "summary_statistics": summary_stats,
            "sample_preview": preview_records
        }

    def _infer_column_type(self, series: pd.Series) -> str:
        if pd.api.types.is_numeric_dtype(series):
            # Check if it is a boolean or binary column
            if series.nunique() <= 2 and set(series.dropna().unique()).issubset({0, 1}):
                return "categorical"
            return "numerical"
        
        # Check datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"

        # Try parsing small sample as datetime if object
        if series.dtype == "object":
            sample_non_null = series.dropna().astype(str).head(10)
            if len(sample_non_null) > 0:
                # Quick regex check for YYYY-MM-DD or DD/MM/YYYY
                date_pattern = r"^(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})"
                matches = sum(1 for s in sample_non_null if re.match(date_pattern, s.strip()))
                if matches >= len(sample_non_null) * 0.8:
                    return "datetime"

            # Check cardinality: if distinct values < 35% of total or unique count < 25 -> categorical
            total_valid = len(series.dropna())
            unique_count = series.nunique()
            if unique_count <= 25 or (total_valid > 0 and (unique_count / total_valid) < 0.35):
                return "categorical"
            return "text"

        return "categorical"

    def _detect_outliers_count(self, clean_series: pd.Series) -> int:
        if len(clean_series) < 4:
            return 0
        q25 = clean_series.quantile(0.25)
        q75 = clean_series.quantile(0.75)
        iqr = q75 - q25
        if iqr == 0:
            return 0
        lower = q25 - 1.5 * iqr
        upper = q75 + 1.5 * iqr
        outliers = clean_series[(clean_series < lower) | (clean_series > upper)]
        return int(len(outliers))

    def _check_sensitive_column(self, col_name: str, series: pd.Series) -> Dict[str, Any]:
        col_lower = col_name.lower().replace(" ", "_")
        for pattern, reason, risk in self.sensitive_patterns:
            if re.search(pattern, col_lower):
                return {
                    "column": col_name,
                    "reason": reason,
                    "risk_level": risk
                }
        
        # Check value pattern for email
        if series.dtype == "object":
            sample = series.dropna().astype(str).head(10)
            for val in sample:
                if re.match(r"[^@]+@[^@]+\.[^@]+", val):
                    return {
                        "column": col_name,
                        "reason": "Email Pattern Detected",
                        "risk_level": "HIGH"
                    }
        return None

    def _compute_quality_score(self, rows: int, cols: int, missing_map: dict, duplicates: int) -> float:
        if rows == 0 or cols == 0:
            return 0.0
        
        score = 100.0
        # Missing values penalty
        total_cells = rows * cols
        total_missing = sum(info["count"] for info in missing_map.values())
        missing_ratio = total_missing / max(total_cells, 1)
        score -= (missing_ratio * 40.0)  # Max 40 points penalty for nulls

        # Duplicates penalty
        dup_ratio = duplicates / max(rows, 1)
        score -= (dup_ratio * 30.0)  # Max 30 points penalty for duplicate rows

        return round(max(5.0, min(100.0, score)), 1)
