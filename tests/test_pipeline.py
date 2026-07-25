import json
import subprocess
import sys
from pathlib import Path


def test_synthetic_pipeline_smoke(tmp_path):
    output_dir = tmp_path / "outputs"
    cmd = [
        sys.executable,
        "scripts/run_synthetic_student_lab.py",
        "--students",
        "32",
        "--weeks",
        "5",
        "--seed",
        "11",
        "--output-dir",
        str(output_dir),
    ]
    subprocess.run(cmd, check=True)
    summary_path = output_dir / "results" / "synthetic_student_analytics_summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["student_count"] == 32
    assert summary["learning_record_count"] == 160
    assert summary["prediction_count"] == 32
    assert summary["audit_log"]["valid"] is True
    assert (output_dir / "reports" / "synthetic_student_analytics_report.md").exists()
