from studentsupport.prediction import predict_support_needs
from studentsupport.privacy import pseudonymize_student_data, quasi_identifier_privacy_audit
from studentsupport.synthetic import SyntheticStudentConfig, generate_synthetic_student_data


def _sample():
    return generate_synthetic_student_data(SyntheticStudentConfig(students=36, weeks=6, seed=5))


def test_pseudonymization_removes_direct_ids():
    data = _sample()
    public = pseudonymize_student_data(data["students"], data["learning_records"], data["access_log"], salt="test")
    assert "synthetic_student_id" not in public["students"].columns
    assert "synthetic_student_id" not in public["learning_records"].columns
    assert "pseudonym_id" in public["students"].columns
    assert public["students"]["pseudonym_id"].nunique() == 36


def test_privacy_audit_and_prediction_outputs():
    data = _sample()
    public = pseudonymize_student_data(data["students"], data["learning_records"], data["access_log"], salt="test")
    privacy = quasi_identifier_privacy_audit(public["students"], k_threshold=4)
    preds = predict_support_needs(public["students"], public["learning_records"])
    assert {"group_size", "small_group_flag", "privacy_risk_score"}.issubset(privacy.columns)
    assert {"support_need_score", "support_need_class", "confidence_proxy"}.issubset(preds.columns)
    assert preds["support_need_score"].between(0, 1).all()
