import pytest

from app.db import get_db
from app.domain import calculate_priority
from tests.conftest import login


@pytest.mark.parametrize(
    ("risk_people", "impact", "expected"),
    [
        (1, "BAJO", "CRITICA"),
        (1, "ALTO", "CRITICA"),
        (0, "ALTO", "ALTA"),
        (0, "BAJO", "NORMAL"),
    ],
)
def test_s02_calculates_priority_on_server(risk_people, impact, expected):
    assert calculate_priority(risk_people, impact) == expected


def create_registered_incident(app, *, impact="ALTO", risk_people=0):
    with app.app_context():
        db = get_db()
        requester_id = db.execute(
            "SELECT id FROM users WHERE username = 'solicitante1'"
        ).fetchone()["id"]
        cursor = db.execute(
            """
            INSERT INTO incidents
            (code, requester_id, location, category, description, impact, risk_people, state, created_at)
            VALUES ('INC-S02-01', ?, 'AULA-201', 'TIC',
                    'Proyector sin señal durante la clase', ?, ?, 'REGISTRADA',
                    '2026-10-08T22:00:00+00:00')
            """,
            (requester_id, impact, risk_people),
        )
        db.execute(
            """
            INSERT INTO events
            (incident_id, actor_id, action, from_state, to_state, detail, created_at)
            VALUES (?, ?, 'CREADA', NULL, 'REGISTRADA', NULL,
                    '2026-10-08T22:00:00+00:00')
            """,
            (cursor.lastrowid, requester_id),
        )
        db.commit()
        return cursor.lastrowid


def technician_id(app, username="tecnico1"):
    with app.app_context():
        return get_db().execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()["id"]


@pytest.mark.integration
def test_s02_coordinator_assigns_active_technician_and_history(app, client):
    incident_id = create_registered_incident(app, impact="ALTO", risk_people=0)
    tech_id = technician_id(app, "tecnico1")

    login(client, username="coordinador")
    response = client.post(
        f"/incidents/{incident_id}/assign",
        data={"technician_id": str(tech_id), "priority": "NORMAL"},
    )

    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        incident = db.execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        event = db.execute(
            "SELECT * FROM events WHERE incident_id = ? ORDER BY id DESC",
            (incident_id,),
        ).fetchone()

        assert incident["state"] == "ASIGNADA"
        assert incident["priority"] == "ALTA"
        assert incident["assigned_technician_id"] == tech_id
        assert event["action"] == "ASIGNADA"
        assert event["from_state"] == "REGISTRADA"
        assert event["to_state"] == "ASIGNADA"


@pytest.mark.integration
def test_s02_non_coordinator_cannot_assign(app, client):
    incident_id = create_registered_incident(app)
    tech_id = technician_id(app)

    login(client, username="solicitante1")
    response = client.post(
        f"/incidents/{incident_id}/assign",
        data={"technician_id": str(tech_id)},
    )

    assert response.status_code == 403

    with app.app_context():
        incident = get_db().execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        assert incident["state"] == "REGISTRADA"
        assert incident["assigned_technician_id"] is None


@pytest.mark.integration
def test_s02_inactive_technician_is_rejected_without_history_change(app, client):
    incident_id = create_registered_incident(app)
    tech_id = technician_id(app, "tecnico2")

    with app.app_context():
        db = get_db()
        db.execute("UPDATE users SET active = 0 WHERE id = ?", (tech_id,))
        db.commit()
        before_events = db.execute(
            "SELECT COUNT(*) FROM events WHERE incident_id = ?", (incident_id,)
        ).fetchone()[0]

    login(client, username="coordinador")
    response = client.post(
        f"/incidents/{incident_id}/assign",
        data={"technician_id": str(tech_id)},
    )

    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        incident = db.execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        after_events = db.execute(
            "SELECT COUNT(*) FROM events WHERE incident_id = ?", (incident_id,)
        ).fetchone()[0]

        assert incident["state"] == "REGISTRADA"
        assert incident["assigned_technician_id"] is None
        assert after_events == before_events


@pytest.mark.integration
def test_s02_second_assignment_is_rejected_and_keeps_original_technician(app, client):
    incident_id = create_registered_incident(app)
    tech1_id = technician_id(app, "tecnico1")
    tech2_id = technician_id(app, "tecnico2")

    login(client, username="coordinador")
    first = client.post(
        f"/incidents/{incident_id}/assign",
        data={"technician_id": str(tech1_id)},
    )
    second = client.post(
        f"/incidents/{incident_id}/assign",
        data={"technician_id": str(tech2_id)},
    )

    assert first.status_code == 302
    assert second.status_code == 302

    with app.app_context():
        db = get_db()
        incident = db.execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        assigned_events = db.execute(
            """
            SELECT COUNT(*) FROM events
            WHERE incident_id = ? AND action = 'ASIGNADA'
            """,
            (incident_id,),
        ).fetchone()[0]

        assert incident["assigned_technician_id"] == tech1_id
        assert incident["state"] == "ASIGNADA"
        assert assigned_events == 1
