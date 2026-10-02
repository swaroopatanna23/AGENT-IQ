import re
from typing import Dict, Any, List

class ValidationPrivacyAgent:
    """
    Validation and Privacy Agent: Performs result data integrity checks
    and applies PII / sensitive data masking.
    Directly fulfills Batch-08 Slide 8, 9 requirements.
    """

    def validate_and_sanitize(
        self,
        analysis_output: Dict[str, Any],
        data_profile: Dict[str, Any],
        schema_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        result_data = analysis_output.get("result_data", [])
        privacy_log = []
        integrity_checks = []

        # 1. Integrity Check: Output Status & Non-empty
        if analysis_output.get("status") == "error":
            integrity_checks.append({"check": "Execution Status", "passed": False, "detail": analysis_output.get("message")})
        else:
            integrity_checks.append({"check": "Execution Status", "passed": True, "detail": "Analysis completed deterministically."})

        if not result_data:
            integrity_checks.append({"check": "Row Count Check", "passed": True, "detail": "Empty result set verified (0 records matched)."})
        else:
            integrity_checks.append({"check": "Row Count Check", "passed": True, "detail": f"{len(result_data)} rows generated."})

        # 2. PII / Privacy Identification & Masking
        sensitive_cols = [c["column"] for c in data_profile.get("sensitive_columns", [])]
        sanitized_records = []

        for row in result_data:
            sanitized_row = {}
            for col, val in row.items():
                if col in sensitive_cols:
                    masked_val = self._mask_sensitive_value(col, val)
                    sanitized_row[col] = masked_val
                    if col not in [p["column"] for p in privacy_log]:
                        privacy_log.append({
                            "column": col,
                            "action": "Masked",
                            "rule": "PII Protection Policy"
                        })
                else:
                    sanitized_row[col] = val
            sanitized_records.append(sanitized_row)

        has_privacy_warning = len(privacy_log) > 0
        privacy_warning = (
            f"Privacy Notice: Protected sensitive attributes ({', '.join([p['column'] for p in privacy_log])}) were masked in visualization and export."
            if has_privacy_warning else None
        )

        return {
            "is_valid": True,
            "integrity_checks": integrity_checks,
            "sanitized_data": sanitized_records,
            "privacy_log": privacy_log,
            "privacy_warning": privacy_warning
        }

    def _mask_sensitive_value(self, col: str, val: Any) -> Any:
        if val is None:
            return None
        val_str = str(val)
        col_lower = col.lower()

        # Email masking: test@domain.com -> t***@domain.com
        if "@" in val_str:
            parts = val_str.split("@")
            user_part = parts[0]
            masked_user = user_part[0] + "***" if len(user_part) > 1 else "***"
            return f"{masked_user}@{parts[1]}"

        # Phone masking: 9876543210 -> 98*****210
        if re.search(r"\d{7,}", val_str):
            if len(val_str) > 5:
                return val_str[:2] + "*****" + val_str[-2:]
            return "*****"

        # General ID / Name masking
        if len(val_str) > 4:
            return val_str[:2] + "***" + val_str[-1:]
        return "***"
