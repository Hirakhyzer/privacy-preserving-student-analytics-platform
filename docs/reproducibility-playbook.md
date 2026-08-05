# Reproducibility Playbook

This playbook defines how to run, document, and report experiments from the **Privacy-Preserving Student Analytics Platform** so another researcher can inspect the workflow.

## 1. Minimum run record

Every experiment should record:

| Field | Example |
|---|---|
| Run name | `synthetic_student_support_seed_42` |
| Dataset type | synthetic fictional student records |
| Number of students | `120` |
| Number of weeks | `10` |
| Random seed | `42` |
| Prediction rule version | current repository commit |
| Privacy checks | pseudonymization + quasi-identifier group-size audit |
| Fairness groups | access level, commute, first-generation proxy groups |
| Intervention rule | human review required, non-punitive wording only |
| Access-audit rule | role, purpose, after-hours, bulk export review |
| Output directory | `outputs/` |
| Boundary statement | synthetic student-support signals only, not real educational decisions |

## 2. Recommended command

```bash
python scripts/run_synthetic_student_lab.py --students 120 --weeks 10 --seed 42
```

## 3. Evidence bundle

A complete run should include:

```text
outputs/results/synthetic_students.csv
outputs/results/synthetic_learning_records.csv
outputs/results/pseudonymized_students.csv
outputs/results/pseudonymized_learning_records.csv
outputs/results/synthetic_support_need_predictions.csv
outputs/results/synthetic_fairness_audit.csv
outputs/results/synthetic_privacy_risk_audit.csv
outputs/results/synthetic_intervention_governance_review.csv
outputs/results/synthetic_access_log.csv
outputs/results/synthetic_access_audit.csv
outputs/results/synthetic_student_analytics_summary.json
outputs/reports/synthetic_student_analytics_report.md
outputs/audit/student_analytics_audit_log.jsonl
outputs/figures/
```

## 4. Interpretation rules

- Treat support scores as review signals, not labels about a student.
- Report fairness metrics separately by subgroup.
- Report privacy-risk flags before discussing predictive results.
- Clearly state that synthetic results do not prove real-world educational impact.
- Preserve human-review and appeal requirements in any discussion of interventions.
- Do not tune thresholds on final test-style evidence after seeing results.

## 5. Checklist before sharing results

- [ ] Seed, student count, week count, and output directory recorded.
- [ ] Synthetic-data boundary stated clearly.
- [ ] Pseudonymized files used for analysis outputs.
- [ ] Small-group privacy risks reviewed.
- [ ] Fairness gaps reported and interpreted cautiously.
- [ ] Access governance flags reviewed.
- [ ] Intervention wording is non-punitive.
- [ ] Audit log saved with the results.
- [ ] No real student deployment claim is made.
