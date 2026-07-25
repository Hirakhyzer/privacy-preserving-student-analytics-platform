from studentsupport.synthetic import SyntheticStudentConfig, generate_synthetic_student_data


def test_synthetic_shapes_and_keys():
    data = generate_synthetic_student_data(SyntheticStudentConfig(students=32, weeks=5, seed=3))
    assert set(data) == {"students", "learning_records", "access_log"}
    assert len(data["students"]) == 32
    assert data["learning_records"]["synthetic_student_id"].nunique() == 32
    assert data["learning_records"]["week"].nunique() == 5
    assert not data["access_log"].empty


def test_invalid_config_rejected():
    try:
        SyntheticStudentConfig(students=10, weeks=3)
    except ValueError:
        assert True
    else:
        raise AssertionError("invalid config should fail")
