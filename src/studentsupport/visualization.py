"""Local plotting helpers for synthetic student-support analytics."""

from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def _save(fig, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_support_need_distribution(predictions: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    data = predictions["support_need_class"].value_counts().sort_index() if not predictions.empty else pd.Series(dtype=int)
    data.plot(kind="bar", ax=ax)
    ax.set_title("Synthetic support-need class distribution")
    ax.set_xlabel("Support class")
    ax.set_ylabel("Student count")
    _save(fig, path)


def plot_fairness_gaps(audit: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    data = audit.groupby("audit_dimension")["support_rate_gap"].max().sort_values(ascending=False) if not audit.empty else pd.Series(dtype=float)
    data.plot(kind="bar", ax=ax)
    ax.set_title("Maximum synthetic support-rate gap by audit dimension")
    ax.set_xlabel("Audit dimension")
    ax.set_ylabel("Support-rate gap")
    _save(fig, path)


def plot_privacy_risk(privacy_audit: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    data = privacy_audit["privacy_risk_score"] if not privacy_audit.empty else pd.Series(dtype=float)
    ax.hist(data, bins=10)
    ax.set_title("Synthetic quasi-identifier privacy-risk scores")
    ax.set_xlabel("Privacy-risk score")
    ax.set_ylabel("Group count")
    _save(fig, path)


def plot_access_audit(access_audit: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    data = access_audit["access_review_reason"].value_counts().head(8) if not access_audit.empty else pd.Series(dtype=int)
    data.plot(kind="bar", ax=ax)
    ax.set_title("Synthetic access audit review reasons")
    ax.set_xlabel("Review reason")
    ax.set_ylabel("Event count")
    _save(fig, path)


def plot_intervention_governance(review: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    data = review["recommended_action"].value_counts() if not review.empty else pd.Series(dtype=int)
    data.plot(kind="bar", ax=ax)
    ax.set_title("Non-punitive intervention governance actions")
    ax.set_xlabel("Recommended action")
    ax.set_ylabel("Count")
    _save(fig, path)
