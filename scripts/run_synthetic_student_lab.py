"""Run the complete synthetic privacy-preserving student analytics lab.

The command uses only fictional student records and access logs. It demonstrates
pseudonymization, quasi-identifier privacy checks, support-need prediction,
fairness auditing, non-punitive intervention governance, access auditing,
reporting, figures, and a hash-chained audit log.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from studentsupport.access import access_summary, audit_access_events
from studentsupport.audit import append_record, verify_log
from studentsupport.config import ensure_output_dirs, set_seed
from studentsupport.fairness import fairness_summary, subgroup_fairness_audit
from studentsupport.intervention import governance_summary, intervention_governance_review
from studentsupport.prediction import predict_support_needs, prediction_summary
from studentsupport.privacy import privacy_summary, pseudonymize_student_data, quasi_identifier_privacy_audit
from studentsupport.reporting import write_report
from studentsupport.synthetic import SyntheticStudentConfig, generate_synthetic_student_data
from studentsupport.visualization import (
    plot_access_audit,
    plot_fairness_gaps,
    plot_intervention_governance,
    plot_privacy_risk,
    plot_support_need_distribution,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a synthetic privacy-preserving student analytics platform lab.")
    parser.add_argument("--students", type=int, default=120)
    parser.add_argument("--weeks", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--pseudonym-salt", default="synthetic-student-support-lab")
    args = parser.parse_args()

    set_seed(args.seed)
    outputs = ensure_output_dirs(args.output_dir)
    data = generate_synthetic_student_data(SyntheticStudentConfig(students=args.students, weeks=args.weeks, seed=args.seed))
    students = data["students"]
    learning_records = data["learning_records"]
    access_log = data["access_log"]

    public = pseudonymize_student_data(students, learning_records, access_log, salt=args.pseudonym_salt)
    public_students = public["students"]
    public_records = public["learning_records"]
    public_access = public["access_log"]

    predictions = predict_support_needs(public_students, public_records)
    fairness = subgroup_fairness_audit(predictions)
    privacy_audit = quasi_identifier_privacy_audit(public_students)
    governance = intervention_governance_review(predictions)
    access_audit = audit_access_events(public_access, predictions)

    summary = {
        "seed": args.seed,
        "student_count": int(len(students)),
        "learning_record_count": int(len(learning_records)),
        "access_event_count": int(len(access_log)),
    }
    summary.update(prediction_summary(predictions))
    summary.update(fairness_summary(fairness))
    summary.update(privacy_summary(privacy_audit))
    summary.update(governance_summary(governance))
    summary.update(access_summary(access_audit))
    summary["data_origin"] = "synthetic fictional student-support records"
    summary["decision_boundary"] = "support review only; not grades, discipline, admissions, surveillance, or automatic intervention"

    students.to_csv(outputs["results"] / "synthetic_students.csv", index=False)
    learning_records.to_csv(outputs["results"] / "synthetic_learning_records.csv", index=False)
    public_students.to_csv(outputs["results"] / "pseudonymized_students.csv", index=False)
    public_records.to_csv(outputs["results"] / "pseudonymized_learning_records.csv", index=False)
    predictions.to_csv(outputs["results"] / "synthetic_support_need_predictions.csv", index=False)
    fairness.to_csv(outputs["results"] / "synthetic_fairness_audit.csv", index=False)
    privacy_audit.to_csv(outputs["results"] / "synthetic_privacy_risk_audit.csv", index=False)
    governance.to_csv(outputs["results"] / "synthetic_intervention_governance_review.csv", index=False)
    access_log.to_csv(outputs["results"] / "synthetic_access_log.csv", index=False)
    access_audit.to_csv(outputs["results"] / "synthetic_access_audit.csv", index=False)

    audit_path = outputs["audit"] / "student_analytics_audit_log.jsonl"
    append_record(audit_path, {**summary, "boundary": "independent synthetic student-support simulator only"})
    summary["audit_log"] = verify_log(audit_path)
    (outputs["results"] / "synthetic_student_analytics_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    write_report(outputs["reports"] / "synthetic_student_analytics_report.md", summary, predictions, fairness, privacy_audit, governance, access_audit)
    plot_support_need_distribution(predictions, outputs["figures"] / "synthetic_support_need_distribution.png")
    plot_fairness_gaps(fairness, outputs["figures"] / "synthetic_fairness_gaps.png")
    plot_privacy_risk(privacy_audit, outputs["figures"] / "synthetic_privacy_risk.png")
    plot_access_audit(access_audit, outputs["figures"] / "synthetic_access_audit.png")
    plot_intervention_governance(governance, outputs["figures"] / "synthetic_intervention_governance.png")

    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
