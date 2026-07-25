"""Non-punitive intervention governance review."""

from __future__ import annotations

import pandas as pd


def intervention_governance_review(predictions: pd.DataFrame) -> pd.DataFrame:
    """Convert prediction signals into safe human-review recommendations."""
    rows = []
    for row in predictions.itertuples(index=False):
        support_class = str(row.support_need_class)
        if support_class == "high_support_review":
            action = "human_support_review_with_multiple_context_sources"
            wording = "Invite the learner to discuss optional support resources; do not imply blame or penalty."
        elif support_class == "support_review":
            action = "offer_low_stakes_support_check_in"
            wording = "Offer a supportive check-in and learning resources; confirm context with the learner."
        elif support_class == "watch":
            action = "monitor_with_minimal_data"
            wording = "Monitor aggregate learning patterns without intrusive tracking or punitive action."
        else:
            action = "routine_support_only"
            wording = "Keep routine support available to all learners."
        rows.append({
            "pseudonym_id": row.pseudonym_id,
            "support_need_class": support_class,
            "support_need_score": float(row.support_need_score),
            "confidence_proxy": float(row.confidence_proxy),
            "uncertainty_flag": int(row.uncertainty_flag),
            "recommended_action": action,
            "safe_support_wording": wording,
            "human_review_required": int(support_class in {"support_review", "high_support_review"} or int(row.uncertainty_flag) == 1),
            "automatic_discipline_allowed": False,
            "automatic_grade_action_allowed": False,
            "automatic_high_stakes_action_allowed": False,
            "governance_status": "human_review_required" if support_class in {"support_review", "high_support_review"} else "safe_routine_support",
        })
    return pd.DataFrame(rows).sort_values(["support_need_score", "human_review_required"], ascending=[False, False]).reset_index(drop=True)


def governance_summary(review: pd.DataFrame) -> dict[str, float | int | str]:
    """Compact intervention governance summary."""
    return {
        "governance_review_rows": int(len(review)),
        "human_review_required_count": int(review["human_review_required"].sum()) if len(review) else 0,
        "automatic_discipline_allowed_count": int(review["automatic_discipline_allowed"].sum()) if len(review) else 0,
        "automatic_grade_action_allowed_count": int(review["automatic_grade_action_allowed"].sum()) if len(review) else 0,
        "intervention_boundary": "supportive human review only; no automatic discipline, grades, or high-stakes action",
    }
