"""Transparent learning-support need prediction baseline."""

from __future__ import annotations

import numpy as np
import pandas as pd


def predict_support_needs(public_students: pd.DataFrame, public_records: pd.DataFrame) -> pd.DataFrame:
    """Score support-review needs from aggregate learning signals."""
    if public_records.empty:
        return pd.DataFrame()
    sorted_records = public_records.sort_values(["pseudonym_id", "week"])
    recent = sorted_records.groupby("pseudonym_id").tail(3)
    early = sorted_records.groupby("pseudonym_id").head(3)
    recent_agg = recent.groupby("pseudonym_id", as_index=False).agg(
        recent_attendance=("attendance_rate", "mean"),
        recent_completion=("assignment_completion_rate", "mean"),
        recent_quiz=("quiz_score", "mean"),
        recent_engagement_minutes=("engagement_minutes", "mean"),
        recent_help_requests=("help_request_count", "sum"),
        recent_late_submissions=("late_submission_count", "sum"),
    )
    early_agg = early.groupby("pseudonym_id", as_index=False).agg(
        early_attendance=("attendance_rate", "mean"),
        early_completion=("assignment_completion_rate", "mean"),
        early_quiz=("quiz_score", "mean"),
    )
    out = public_students.merge(recent_agg, on="pseudonym_id", how="left").merge(early_agg, on="pseudonym_id", how="left")
    out = out.fillna(0)
    out["attendance_drop"] = (out["early_attendance"] - out["recent_attendance"]).clip(lower=0)
    out["completion_drop"] = (out["early_completion"] - out["recent_completion"]).clip(lower=0)
    out["quiz_drop"] = ((out["early_quiz"] - out["recent_quiz"]) / 100).clip(lower=0)
    low_attendance = (1 - out["recent_attendance"]).clip(0, 1)
    low_completion = (1 - out["recent_completion"]).clip(0, 1)
    low_quiz = (1 - out["recent_quiz"] / 100).clip(0, 1)
    low_engagement = (1 - out["recent_engagement_minutes"] / 360).clip(0, 1)
    help_signal = (out["recent_help_requests"] / 5).clip(0, 1)
    late_signal = (out["recent_late_submissions"] / 6).clip(0, 1)
    out["support_need_score"] = np.clip(
        0.22 * low_attendance
        + 0.24 * low_completion
        + 0.18 * low_quiz
        + 0.12 * low_engagement
        + 0.10 * help_signal
        + 0.07 * late_signal
        + 0.04 * out["attendance_drop"]
        + 0.03 * out["completion_drop"],
        0,
        1,
    ).round(4)
    out["support_need_class"] = out["support_need_score"].apply(_support_class)
    out["confidence_proxy"] = np.clip(0.52 + 0.22 * (out["recent_attendance"] > 0) + 0.20 * (out["recent_completion"] > 0) + 0.06 * (out["recent_quiz"] > 0), 0, 1).round(4)
    out["uncertainty_flag"] = (out["confidence_proxy"] < 0.75).astype(int)
    out["risk_drivers"] = out.apply(_drivers, axis=1)
    keep = [
        "pseudonym_id", "program_track", "access_band", "commute_band", "first_generation_proxy", "age_band",
        "support_need_score", "support_need_class", "confidence_proxy", "uncertainty_flag", "risk_drivers",
        "recent_attendance", "recent_completion", "recent_quiz", "recent_engagement_minutes", "recent_help_requests",
    ]
    return out[keep].sort_values(["support_need_score", "uncertainty_flag"], ascending=[False, False]).reset_index(drop=True)


def prediction_summary(predictions: pd.DataFrame) -> dict[str, float | int | str]:
    return {
        "prediction_count": int(len(predictions)),
        "support_review_count": int(predictions["support_need_class"].isin(["support_review", "high_support_review"]).sum()) if len(predictions) else 0,
        "high_support_review_count": int((predictions["support_need_class"] == "high_support_review").sum()) if len(predictions) else 0,
        "mean_support_need_score": float(predictions["support_need_score"].mean()) if len(predictions) else 0.0,
        "uncertainty_flag_count": int(predictions["uncertainty_flag"].sum()) if len(predictions) else 0,
    }


def _support_class(score: float) -> str:
    if score >= 0.76:
        return "high_support_review"
    if score >= 0.58:
        return "support_review"
    if score >= 0.36:
        return "watch"
    return "routine_support"


def _drivers(row: pd.Series) -> str:
    drivers: list[str] = []
    if row.recent_attendance < 0.62:
        drivers.append("attendance_pattern")
    if row.recent_completion < 0.60:
        drivers.append("completion_pattern")
    if row.recent_quiz < 62:
        drivers.append("assessment_pattern")
    if row.recent_engagement_minutes < 145:
        drivers.append("engagement_pattern")
    if row.recent_help_requests >= 3:
        drivers.append("help_seeking_signal")
    return "|".join(drivers) if drivers else "no_high_priority_driver"
