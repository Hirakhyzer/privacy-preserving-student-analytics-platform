"""Fairness audits for support-need predictions."""

from __future__ import annotations

import pandas as pd

AUDIT_GROUPS = ["access_band", "commute_band", "first_generation_proxy", "preferred_modality"]


def subgroup_fairness_audit(predictions: pd.DataFrame) -> pd.DataFrame:
    """Audit support-rate and score gaps across key synthetic subgroups."""
    if predictions.empty:
        return pd.DataFrame(columns=["audit_dimension", "subgroup", "student_count", "support_review_rate", "mean_support_need_score"])
    rows = []
    for dimension in AUDIT_GROUPS:
        if dimension not in predictions.columns:
            continue
        for subgroup, group in predictions.groupby(dimension):
            support_rate = float(group["support_need_class"].isin(["support_review", "high_support_review"]).mean())
            rows.append({
                "audit_dimension": dimension,
                "subgroup": str(subgroup),
                "student_count": int(len(group)),
                "support_review_rate": support_rate,
                "mean_support_need_score": float(group["support_need_score"].mean()),
                "uncertainty_rate": float(group["uncertainty_flag"].mean()),
            })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    gaps = out.groupby("audit_dimension").agg(
        support_rate_gap=("support_review_rate", lambda s: float(s.max() - s.min())),
        mean_score_gap=("mean_support_need_score", lambda s: float(s.max() - s.min())),
        uncertainty_gap=("uncertainty_rate", lambda s: float(s.max() - s.min())),
    ).reset_index()
    out = out.merge(gaps, on="audit_dimension", how="left")
    out["fairness_review_flag"] = ((out["support_rate_gap"] > 0.18) | (out["mean_score_gap"] > 0.12)).astype(int)
    out["review_interpretation"] = out["fairness_review_flag"].map({1: "review_support_policy_for_group_gap", 0: "no_large_synthetic_gap_detected"})
    return out.sort_values(["fairness_review_flag", "audit_dimension", "support_review_rate"], ascending=[False, True, False]).reset_index(drop=True)


def fairness_summary(audit: pd.DataFrame) -> dict[str, float | int | str]:
    """Compact fairness summary."""
    return {
        "fairness_audit_rows": int(len(audit)),
        "fairness_review_flag_count": int(audit["fairness_review_flag"].sum()) if len(audit) else 0,
        "max_support_rate_gap": float(audit["support_rate_gap"].max()) if len(audit) else 0.0,
        "max_mean_score_gap": float(audit["mean_score_gap"].max()) if len(audit) else 0.0,
        "fairness_boundary": "descriptive subgroup audit; not proof of fairness or unfairness",
    }
