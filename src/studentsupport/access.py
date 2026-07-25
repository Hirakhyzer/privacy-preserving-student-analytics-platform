"""Access-log auditing for synthetic student-support analytics."""

from __future__ import annotations

import pandas as pd

ALLOWED_ROLES = {"educator", "advisor", "support_staff", "analytics_admin"}
SUPPORT_PURPOSES = {"student_support", "course_feedback", "quality_review"}


def audit_access_events(public_access_log: pd.DataFrame, predictions: pd.DataFrame) -> pd.DataFrame:
    """Flag unusual synthetic access events for review."""
    if public_access_log.empty:
        return pd.DataFrame()
    sensitivity = predictions[["pseudonym_id", "support_need_class", "support_need_score"]].copy() if not predictions.empty else pd.DataFrame(columns=["pseudonym_id", "support_need_class", "support_need_score"])
    out = public_access_log.merge(sensitivity, on="pseudonym_id", how="left")
    out["support_need_class"] = out["support_need_class"].fillna("unknown")
    out["support_need_score"] = out["support_need_score"].fillna(0.0)
    out["unusual_role_flag"] = (~out["actor_role"].isin(ALLOWED_ROLES)).astype(int)
    out["unsupported_purpose_flag"] = (~out["access_purpose"].isin(SUPPORT_PURPOSES)).astype(int)
    out["after_hours_flag"] = ((out["access_hour"] < 7) | (out["access_hour"] > 20)).astype(int)
    out["bulk_export_flag"] = ((out["action"] == "export") | (out["records_accessed"] >= 20)).astype(int)
    out["high_sensitivity_record_flag"] = out["support_need_class"].isin(["support_review", "high_support_review"]).astype(int)
    out["access_risk_score"] = (
        0.30 * out["unusual_role_flag"]
        + 0.25 * out["unsupported_purpose_flag"]
        + 0.15 * out["after_hours_flag"]
        + 0.18 * out["bulk_export_flag"]
        + 0.12 * out["high_sensitivity_record_flag"]
    ).clip(0, 1).round(4)
    out["suspicious_access_flag"] = (out["access_risk_score"] >= 0.35).astype(int)
    out["access_review_reason"] = out.apply(_reason, axis=1)
    return out.sort_values(["suspicious_access_flag", "access_risk_score"], ascending=[False, False]).reset_index(drop=True)


def access_summary(access_audit: pd.DataFrame) -> dict[str, float | int | str]:
    """Compact access governance summary."""
    return {
        "access_audit_rows": int(len(access_audit)),
        "suspicious_access_event_count": int(access_audit["suspicious_access_flag"].sum()) if len(access_audit) else 0,
        "after_hours_access_count": int(access_audit["after_hours_flag"].sum()) if len(access_audit) else 0,
        "unsupported_purpose_count": int(access_audit["unsupported_purpose_flag"].sum()) if len(access_audit) else 0,
        "bulk_export_review_count": int(access_audit["bulk_export_flag"].sum()) if len(access_audit) else 0,
    }


def _reason(row: pd.Series) -> str:
    reasons = []
    if row.unusual_role_flag:
        reasons.append("unusual_role")
    if row.unsupported_purpose_flag:
        reasons.append("unsupported_purpose")
    if row.after_hours_flag:
        reasons.append("after_hours")
    if row.bulk_export_flag:
        reasons.append("bulk_export")
    if row.high_sensitivity_record_flag:
        reasons.append("support_record_sensitivity")
    return "|".join(reasons) if reasons else "routine_support_access"
