"""Pseudonymization and privacy-risk checks."""

from __future__ import annotations

import hashlib
import pandas as pd

QUASI_IDENTIFIERS = ["program_track", "access_band", "commute_band", "first_generation_proxy", "age_band", "preferred_modality"]


def pseudonymize_student_data(
    students: pd.DataFrame,
    records: pd.DataFrame,
    access_log: pd.DataFrame,
    salt: str = "synthetic-student-support-lab",
) -> dict[str, pd.DataFrame]:
    """Replace direct synthetic identifiers with salted pseudonymous IDs."""
    mapping = {sid: _pseudo_id(str(sid), salt) for sid in students["synthetic_student_id"].astype(str)}
    public_students = students.copy()
    public_students["pseudonym_id"] = public_students["synthetic_student_id"].map(mapping)
    public_students = public_students.drop(columns=["synthetic_student_id"])

    public_records = records.copy()
    public_records["pseudonym_id"] = public_records["synthetic_student_id"].map(mapping)
    public_records = public_records.drop(columns=["synthetic_student_id"])

    public_access = access_log.copy()
    public_access["pseudonym_id"] = public_access["synthetic_student_id"].map(mapping)
    public_access = public_access.drop(columns=["synthetic_student_id"])
    return {"students": public_students, "learning_records": public_records, "access_log": public_access}


def quasi_identifier_privacy_audit(public_students: pd.DataFrame, k_threshold: int = 5) -> pd.DataFrame:
    """Run a k-anonymity-style group-size audit for quasi-identifiers."""
    if public_students.empty:
        return pd.DataFrame(columns=QUASI_IDENTIFIERS + ["group_size", "k_threshold", "small_group_flag", "privacy_risk_score"])
    grouped = public_students.groupby(QUASI_IDENTIFIERS, dropna=False).size().reset_index(name="group_size")
    grouped["k_threshold"] = int(k_threshold)
    grouped["small_group_flag"] = (grouped["group_size"] < k_threshold).astype(int)
    grouped["privacy_risk_score"] = (1 - (grouped["group_size"] / max(k_threshold, 1))).clip(lower=0, upper=1).round(4)
    grouped["privacy_review_action"] = grouped["small_group_flag"].map({1: "generalize_or_suppress_small_group", 0: "acceptable_synthetic_group_size"})
    return grouped.sort_values(["privacy_risk_score", "group_size"], ascending=[False, True]).reset_index(drop=True)


def privacy_summary(privacy_audit: pd.DataFrame) -> dict[str, float | int | str]:
    """Compact privacy summary."""
    return {
        "privacy_group_count": int(len(privacy_audit)),
        "small_privacy_group_count": int(privacy_audit["small_group_flag"].sum()) if len(privacy_audit) else 0,
        "max_privacy_risk_score": float(privacy_audit["privacy_risk_score"].max()) if len(privacy_audit) else 0.0,
        "privacy_boundary": "pseudonymized synthetic records only; no direct student identifiers in public outputs",
    }


def _pseudo_id(value: str, salt: str) -> str:
    digest = hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()[:16]
    return f"PSEUDO-{digest}"
