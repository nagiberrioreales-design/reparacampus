import pytest

from app.db import get_db
from tests.conftest import login


VALID_FORM = {
    "location": "LAB-01",
    "category": "ELECTRICIDAD",
    "description": "Cable expuesto cerca del laboratorio",
    "impact": "ALTO",
    "risk_people": "true",
}


@pytest.mark.integration
def test_s01_registration_persists_incident_and_history(app, client):
    login(client)
    response = client.post("/incidents/new", data=VALID_FORM)

    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        incident = db.execute("SELECT * FROM incidents").fetchone()
        event = db.execute("SELECT * FROM events").fetchone()

        assert incident is not None
        assert incident["state"] == "REGISTRADA"
        assert incident["location"] == "LAB-01"
        assert incident["risk_people"] == 1
        assert incident["code"].startswith("INC-")

        assert event is not None
        assert event["incident_id"] == incident["id"]
        assert event["action"] == "CREADA"
        assert event["from_state"] is None
        assert event["to_state"] == "REGISTRADA"


@pytest.mark.integration
def test_s01_non_requester_cannot_register_and_database_stays_unchanged(app, client):
    login(client, username="coordinador")
    response = client.post("/incidents/new", data=VALID_FORM)

    assert response.status_code == 403

    with app.app_context():
        db = get_db()
        assert db.execute("SELECT COUNT(*) FROM incidents").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0


@pytest.mark.integration
def test_s01_ignores_forged_author_and_escapes_stored_text(app, client):
    login(client, username="solicitante1")

    form = dict(VALID_FORM)
    form["description"] = "<script>alert(1)</script> daño en toma eléctrica"
    form["requester_id"] = "2"

    response = client.post("/incidents/new", data=form)
    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        requester = db.execute(
            "SELECT id FROM users WHERE username = 'solicitante1'"
        ).fetchone()
        incident = db.execute("SELECT * FROM incidents").fetchone()
        assert incident["requester_id"] == requester["id"]

    page = client.get("/incidents/")
    assert page.status_code == 200
    assert b"<script>" not in page.data
    assert b"&lt;script&gt;" in page.data


@pytest.mark.integration
def test_persistence_survives_application_restart(app, client):
    login(client)
    response = client.post("/incidents/new", data=VALID_FORM)
    assert response.status_code == 302

    database_path = app.config["DATABASE"]

    from app import create_app
    restarted_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "restart-test-secret",
            "DATABASE": database_path,
        }
    )

    with restarted_app.app_context():
        db = get_db()
        incident_count = db.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
        event_count = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]

        assert incident_count == 1
        assert event_count == 1
