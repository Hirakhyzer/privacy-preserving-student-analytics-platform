"""Markdown report generation."""

from __future__ import annotations

from pathlib import Path
import pandas as pd


def _table(frame: pd.DataFrame, limit: int = 10) -> str:
    if frame.empty:
        return "No rows generated."
    return frame.head(limit).to_markdown(index=False)


def write_report(
    path: str | Path,
    summary: dict,
    predictions: pd.DataFrame,
    fairness: pd.DataFrame,
    privacy_audit: pd.DataFrame,
    governance: pd.DataFrame,
    access_audit: pd.DataFrame,
) -> None:
    """Write a compact student-support analytics report."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Synthetic Privacy-Preserving Student Analytics Report",
        "",
        "> Independent student-support review simulator only. This report is not a grade, discipline, admissions, surveillance, or automatic intervention decision.",
        "",
        "## Summary",
        "",
        _table(pd.DataFrame([summary]).T.reset_index().rename(columns={"index": "metric", 0: "value"}), limit=40),
        "",
        "## Highest support-review signals",
        "",
        _table(predictions[["pseudonym_id", "support_need_score", "support_need_class", "confidence_proxy", "risk_drivers"]], 12) if not predictions.empty else "No predictions.",
        "",
        "## Fairness audit",
        "",
        _table(fairness, 12),
        "",
        "## Privacy risk audit",
        "",
        _table(privacy_audit, 12),
        "",
        "## Intervention governance review",
        "",
        _table(governance[["pseudonym_id", "recommended_action", "human_review_required", "automatic_discipline_allowed", "automatic_grade_action_allowed"]], 12) if not governance.empty else "No governance rows.",
        "",
        "## Access audit",
        "",
        _table(access_audit[["access_event_id", "actor_role", "access_purpose", "access_risk_score", "suspicious_access_flag", "access_review_reason"]], 12) if not access_audit.empty else "No access audit rows.",
        "",
        "## Required interpretation boundary",
        "",
        "Use these outputs for transparent, supportive, human-reviewed research only. Do not use them for automatic grades, discipline, admissions, surveillance, or high-stakes decisions.",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
