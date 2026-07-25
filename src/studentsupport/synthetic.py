"""Deterministic synthetic student-support data.

All students, activity records, and access events are fictional and intended for
privacy-preserving analytics research without exposing real education data.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

PROGRAM_TRACKS = ["computing", "business", "health_science", "engineering", "social_science"]
ACCESS_BANDS = ["high_resource_access", "moderate_resource_access", "limited_resource_access"]
COMMUTE_BANDS = ["near_campus", "mixed_commute", "long_commute"]
FIRST_GEN = ["continuing_generation_proxy", "first_generation_proxy"]
ROLES = ["educator", "advisor", "support_staff", "analytics_admin", "external_viewer"]
PURPOSES = ["student_support", "course_feedback", "quality_review", "bulk_export", "unrelated_lookup"]


@dataclass(frozen=True)
class SyntheticStudentConfig:
    students: int = 120
    weeks: int = 10
    seed: int = 42

    def __post_init__(self) -> None:
        if self.students < 24:
            raise ValueError("Use at least 24 synthetic students for subgroup fairness review.")
        if self.weeks < 4:
            raise ValueError("Use at least 4 weeks of records for trend analysis.")


def generate_synthetic_student_data(config: SyntheticStudentConfig | None = None) -> dict[str, pd.DataFrame]:
    """Generate fictional student profiles, weekly records, and access logs."""
    cfg = config or SyntheticStudentConfig()
    rng = np.random.default_rng(cfg.seed)
    students = _students(cfg, rng)
    records = _learning_records(students, cfg, rng)
    access_log = _access_log(students, cfg, rng)
    return {"students": students, "learning_records": records, "access_log": access_log}


def _students(cfg: SyntheticStudentConfig, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for idx in range(cfg.students):
        access = ACCESS_BANDS[idx % len(ACCESS_BANDS)]
        commute = COMMUTE_BANDS[(idx + idx // 5) % len(COMMUTE_BANDS)]
        first_gen = FIRST_GEN[idx % len(FIRST_GEN)]
        program = PROGRAM_TRACKS[(idx * 2 + idx // 7) % len(PROGRAM_TRACKS)]
        rows.append({
            "synthetic_student_id": f"S-{idx + 1:05d}",
            "program_track": program,
            "access_band": access,
            "commute_band": commute,
            "first_generation_proxy": first_gen,
            "age_band": ["traditional_age", "adult_learner"][idx % 4 == 0],
            "preferred_modality": ["in_person", "hybrid", "online"][idx % 3],
            "baseline_engagement": round(float(np.clip(rng.normal(0.66, 0.14), 0.25, 0.96)), 3),
            "support_resource_access": round(float(np.clip(0.78 - 0.16 * ACCESS_BANDS.index(access) + rng.normal(0, 0.08), 0.18, 0.95)), 3),
        })
    return pd.DataFrame(rows)


def _learning_records(students: pd.DataFrame, cfg: SyntheticStudentConfig, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for student in students.itertuples(index=False):
        access_penalty = {"high_resource_access": 0.03, "moderate_resource_access": -0.02, "limited_resource_access": -0.10}[student.access_band]
        commute_penalty = {"near_campus": 0.03, "mixed_commute": -0.02, "long_commute": -0.08}[student.commute_band]
        first_gen_shift = -0.03 if student.first_generation_proxy == "first_generation_proxy" else 0.01
        base = float(np.clip(student.baseline_engagement + access_penalty + commute_penalty + first_gen_shift, 0.15, 0.98))
        for week in range(1, cfg.weeks + 1):
            fatigue = -0.015 * max(0, week - cfg.weeks * 0.55)
            shock = rng.normal(0, 0.055)
            engagement = float(np.clip(base + fatigue + shock, 0.05, 1.0))
            attendance = float(np.clip(0.72 * engagement + 0.18 * student.support_resource_access + rng.normal(0, 0.08), 0.0, 1.0))
            completion = float(np.clip(0.66 * engagement + 0.23 * student.support_resource_access + rng.normal(0, 0.09), 0.0, 1.0))
            quiz = float(np.clip(52 + 42 * (0.55 * completion + 0.45 * attendance) + rng.normal(0, 6.5), 0, 100))
            help_requests = int(max(0, rng.poisson(0.5 + 1.6 * max(0, 0.55 - engagement))))
            rows.append({
                "synthetic_student_id": student.synthetic_student_id,
                "week": week,
                "attendance_rate": round(attendance, 3),
                "engagement_minutes": int(np.clip(70 + 260 * engagement + rng.normal(0, 30), 10, 420)),
                "assignment_completion_rate": round(completion, 3),
                "quiz_score": round(quiz, 2),
                "help_request_count": help_requests,
                "late_submission_count": int(max(0, rng.poisson(1.2 * max(0, 0.72 - completion)))) ,
                "platform_access_count": int(np.clip(3 + 18 * engagement + rng.normal(0, 3), 0, 35)),
            })
    return pd.DataFrame(rows)


def _access_log(students: pd.DataFrame, cfg: SyntheticStudentConfig, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    event_count = max(80, int(cfg.students * 1.4))
    student_ids = students["synthetic_student_id"].to_numpy()
    for idx in range(event_count):
        role = str(rng.choice(ROLES, p=[0.32, 0.28, 0.20, 0.14, 0.06]))
        purpose = str(rng.choice(PURPOSES, p=[0.58, 0.16, 0.12, 0.08, 0.06]))
        hour = int(rng.choice(range(24), p=_hour_probs()))
        rows.append({
            "access_event_id": f"A-{idx + 1:05d}",
            "synthetic_student_id": str(rng.choice(student_ids)),
            "actor_role": role,
            "access_purpose": purpose,
            "access_hour": hour,
            "action": str(rng.choice(["view_summary", "view_detail", "export", "annotate"], p=[0.50, 0.29, 0.09, 0.12])),
            "records_accessed": int(rng.integers(1, 45 if purpose == "bulk_export" else 8)),
        })
    return pd.DataFrame(rows)


def _hour_probs() -> np.ndarray:
    probs = np.ones(24) * 0.015
    probs[8:18] = 0.075
    probs[18:22] = 0.028
    probs = probs / probs.sum()
    return probs
