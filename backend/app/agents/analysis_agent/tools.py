import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

class AnalysisTools:
    """
    Controlled deterministic analytical tools using Pandas, NumPy, and SciPy.
    Strictly zero arbitrary code execution.
    """

    @staticmethod
    def filter_data(df: pd.DataFrame, filters: list) -> pd.DataFrame:
        if not filters or df.empty:
            return df
        filtered = df.copy()
        for f in filters:
            col = f.column if hasattr(f, "column") else f.get("column")
            op = f.operator if hasattr(f, "operator") else f.get("operator", "eq")
            val = f.value if hasattr(f, "value") else f.get("value")

            if col not in filtered.columns:
                continue

            try:
                if op == "eq":
                    filtered = filtered[filtered[col].astype(str).str.lower() == str(val).lower()]
                elif op == "neq":
                    filtered = filtered[filtered[col].astype(str).str.lower() != str(val).lower()]
                elif op == "gt":
                    filtered = filtered[pd.to_numeric(filtered[col], errors='coerce') > float(val)]
                elif op == "gte":
                    filtered = filtered[pd.to_numeric(filtered[col], errors='coerce') >= float(val)]
                elif op == "lt":
                    filtered = filtered[pd.to_numeric(filtered[col], errors='coerce') < float(val)]
                elif op == "lte":
                    filtered = filtered[pd.to_numeric(filtered[col], errors='coerce') <= float(val)]
                elif op == "contains":
                    filtered = filtered[filtered[col].astype(str).str.contains(str(val), case=False, na=False)]
                elif op == "in" and isinstance(val, list):
                    filtered = filtered[filtered[col].isin(val)]
            except Exception as e:
                print(f"Filter error on {col} {op} {val}: {e}")
        return filtered

    @staticmethod
    def group_and_aggregate(
        df: pd.DataFrame,
        group_by: List[str],
        target_cols: List[str],
        agg_func: str = "avg"
    ) -> pd.DataFrame:
        if df.empty or not group_by:
            return df

        valid_groups = [g for g in group_by if g in df.columns]
        valid_targets = [t for t in target_cols if t in df.columns and pd.api.types.is_numeric_dtype(df[t])]

        if not valid_groups:
            return df

        agg_mapping = {
            "avg": "mean",
            "mean": "mean",
            "sum": "sum",
            "count": "count",
            "max": "max",
            "min": "min",
            "median": "median"
        }
        func = agg_mapping.get(agg_func.lower(), "mean")

        if not valid_targets:
            # Count records per group
            result = df.groupby(valid_groups, as_index=False).size()
            result.rename(columns={"size": "count"}, inplace=True)
            return result

        agg_dict = {t: func for t in valid_targets}
        result = df.groupby(valid_groups, as_index=False).agg(agg_dict)
        # Round numerical output
        for t in valid_targets:
            result[t] = result[t].round(2)
        return result

    @staticmethod
    def sort_data(df: pd.DataFrame, sort_col: str, ascending: bool = True, limit: Optional[int] = None) -> pd.DataFrame:
        if df.empty or sort_col not in df.columns:
            return df
        sorted_df = df.sort_values(by=sort_col, ascending=ascending)
        if limit and limit > 0:
            return sorted_df.head(limit)
        return sorted_df

    @staticmethod
    def calculate_statistics(df: pd.DataFrame, col: str) -> Dict[str, float]:
        if df.empty or col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            return {}
        s = df[col].dropna()
        if len(s) == 0:
            return {}
        return {
            "count": int(len(s)),
            "sum": round(float(s.sum()), 2),
            "mean": round(float(s.mean()), 2),
            "median": round(float(s.median()), 2),
            "min": round(float(s.min()), 2),
            "max": round(float(s.max()), 2),
            "std": round(float(s.std()), 2) if len(s) > 1 else 0.0
        }

    @staticmethod
    def calculate_correlation(df: pd.DataFrame, col1: str, col2: str) -> Dict[str, Any]:
        if df.empty or col1 not in df.columns or col2 not in df.columns:
            return {"correlation": None, "strength": "unknown"}
        s1 = pd.to_numeric(df[col1], errors="coerce")
        s2 = pd.to_numeric(df[col2], errors="coerce")
        valid_mask = s1.notna() & s2.notna()
        if valid_mask.sum() < 2:
            return {"correlation": None, "strength": "insufficient data"}
        corr = float(s1[valid_mask].corr(s2[valid_mask]))
        if abs(corr) >= 0.7:
            strength = "strong"
        elif abs(corr) >= 0.4:
            strength = "moderate"
        elif abs(corr) >= 0.2:
            strength = "weak"
        else:
            strength = "negligible"
        return {"correlation": round(corr, 3), "strength": strength}

    @staticmethod
    def calculate_trend(df: pd.DataFrame, date_col: str, metric_col: str, freq: str = "ME") -> pd.DataFrame:
        if df.empty or date_col not in df.columns or metric_col not in df.columns:
            return df
        temp = df.copy()
        temp[date_col] = pd.to_datetime(temp[date_col], errors="coerce")
        temp = temp.dropna(subset=[date_col, metric_col])
        if temp.empty:
            return pd.DataFrame()
        temp.set_index(date_col, inplace=True)
        resampled = temp[metric_col].resample(freq).sum().reset_index()
        resampled[date_col] = resampled[date_col].dt.strftime("%Y-%m")
        resampled[metric_col] = resampled[metric_col].round(2)
        return resampled

    @staticmethod
    def distribution_analysis(df: pd.DataFrame, col: str, bins: int = 10) -> Dict[str, Any]:
        if df.empty or col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            return {}
        s = df[col].dropna()
        counts, bin_edges = np.histogram(s, bins=bins)
        distribution_data = []
        for i in range(len(counts)):
            label = f"{round(bin_edges[i], 1)} - {round(bin_edges[i+1], 1)}"
            distribution_data.append({"bin": label, "count": int(counts[i])})
        return {
            "bins": distribution_data,
            "min": float(s.min()),
            "max": float(s.max()),
            "median": float(s.median())
        }
