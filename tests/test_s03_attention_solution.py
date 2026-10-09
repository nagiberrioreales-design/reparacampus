import pytest

from app.db import get_db
from app.domain import validate_solution
from tests.conftest import login


def create_assigned_incident(app, *, technician_username="tecnico1", state="ASIGNADA"):
    with app.app_context():
        db = get_db()
        requester_id = db.execute(
            "SELECT id FROM users WHERE username = 'solicitante1'"
        ).fetchone()["id"]
        technician_id = db.execute(
            "SELECT id FROM users WHERE username = ?",
            (technician_username,),
        ).fetchone()["id"]
        cursor = db.execute(
            """
            INSERT INTO incidents
            (code, requester_id, location, category, description, impact,
             risk_people, priority, state, assigned_technician_id, created_at)
            VALUES ('INC-S03-01', ?, 'LAB-01', 'ELECTRICIDAD',
                    'Toma eléctrica con falla intermitente', 'ALTO', 1,
                    'CRITICA', ?, ?, '2026-10-08T22:30:00+00:00')
            """,
            (requester_id, state, technician_id),
        )
        incident_id = cursor.lastrowid
        db.execute(
            """
            INSERT INTO events
            (incident_id, actor_id, action, from_state, to_state, detail, created_at)
            VALUES (?, ?, 'ASIGNADA', 'REGISTRADA', 'ASIGNADA',
                    'Asignada para prueba S03', '2026-10-08T22:31:00+00:00')
            """,
            (incident_id, requester_id),
        )
        db.commit()
        return incident_id


@pytest.mark.parametrize(
    ("value", "valid"),
    [
        ("x" * 19, False),
        ("x" * 20, True),
        ("x" * 800, True),
        ("x" * 801, False),
    ],
)
def test_s03_solution_limits(value, valid):
    _cleaned, error = validate_solution(value)
    assert (error is None) is valid


@pytest.mark.integration
def test_s03_assigned_technician_starts_attention(app, client):
    incident_id = create_assigned_incident(app)

    login(client, username="tecnico1")
    response = client.post(f"/incidents/{incident_id}/start")

    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        incident = db.execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        event = db.execute(
            """
            SELECT * FROM events
            WHERE incident_id = ? AND action = 'INICIO_ATENCION'
            """,
            (incident_id,),
        ).fetchone()

        assert incident["state"] == "EN_ATENCION"
        assert event is not None
        assert event["from_state"] == "ASIGNADA"
        assert event["to_state"] == "EN_ATENCION"


@pytest.mark.integration
def test_s03_other_technician_cannot_start_attention(app, client):
    incident_id = create_assigned_incident(app, technician_username="tecnico1")

    login(client, username="tecnico2")
    response = client.post(f"/incidents/{incident_id}/start")

    assert response.status_code == 403

    with app.app_context():
        incident = get_db().execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        assert incident["state"] == "ASIGNADA"


@pytest.mark.integration
def test_s03_solution_moves_to_pending_validation_and_keeps_history(app, client):
    incident_id = create_assigned_incident(app, state="EN_ATENCION")
    solution = "Se reemplazó la toma dañada y se verificó el funcionamiento."

    login(client, username="tecnico1")
    response = client.post(
        f"/incidents/{incident_id}/solution",
        data={"solution": solution},
    )

    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        incident = db.execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        saved_solution = db.execute(
            "SELECT * FROM solutions WHERE incident_id = ?",
            (incident_id,),
        ).fetchone()
        event = db.execute(
            """
            SELECT * FROM events
            WHERE incident_id = ? AND action = 'SOLUCION_PROPUESTA'
            """,
            (incident_id,),
        ).fetchone()

        assert incident["state"] == "PENDIENTE_VALIDACION"
        assert saved_solution["text"] == solution
        assert event["from_state"] == "EN_ATENCION"
        assert event["to_state"] == "PENDIENTE_VALIDACION"


@pytest.mark.integration
def test_s03_invalid_solution_keeps_state_and_does_not_create_solution(app, client):
    incident_id = create_assigned_incident(app, state="EN_ATENCION")

    login(client, username="tecnico1")
    response = client.post(
        f"/incidents/{incident_id}/solution",
        data={"solution": "Muy corta"},
    )

    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        incident = db.execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        count = db.execute(
            "SELECT COUNT(*) FROM solutions WHERE incident_id = ?",
            (incident_id,),
        ).fetchone()[0]

        assert incident["state"] == "EN_ATENCION"
        assert count == 0
