import pytest

from app.domain import validate_new_incident


def valid_data(**changes):
    data = {
        "location": "LAB-01",
        "category": "ELECTRICIDAD",
        "description": "x" * 20,
        "impact": "ALTO",
        "risk_people": "true",
    }
    data.update(changes)
    return data


def test_s01_accepts_valid_data():
    cleaned, errors = validate_new_incident(valid_data())
    assert errors == {}
    assert cleaned["description"] == "x" * 20
    assert cleaned["risk_people"] is True


@pytest.mark.parametrize("length", [0, 19, 501])
def test_s01_rejects_description_outside_limits(length):
    _cleaned, errors = validate_new_incident(valid_data(description="x" * length))
    assert "description" in errors


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("location", "CAFETERIA"),
        ("category", "PINTURA"),
        ("impact", "MEDIO"),
        ("risk_people", "quizas"),
    ],
)
def test_s01_rejects_invalid_catalog_or_boolean(field, value):
    _cleaned, errors = validate_new_incident(valid_data(**{field: value}))
    assert field in errors


def test_s01_trims_external_spaces_before_counting():
    cleaned, errors = validate_new_incident(valid_data(description="   " + ("z" * 20) + "   "))
    assert errors == {}
    assert cleaned["description"] == "z" * 20


def test_s01_accepts_exactly_500_characters():
    cleaned, errors = validate_new_incident(valid_data(description="x" * 500))
    assert errors == {}
    assert len(cleaned["description"]) == 500
