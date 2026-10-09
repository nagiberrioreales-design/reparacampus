from datetime import datetime, timedelta, timezone

import pytest

from app.db import get_db
from app.domain import validate_reason
from tests.conftest import login


def requester_id(app, username="solicitante1"):
    with app.app_context():
        return get_db().execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()["id"]


def technician_id(app, username="tecnico1"):
    with app.app_context():
        return get_db().execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()["id"]


def create_pending_incident(app, *, requester="solicitante1"):
    with app.app_context():
        db = get_db()
        req_id = db.execute(
            "SELECT id FROM users WHERE username = ?", (requester,)
        ).fetchone()["id"]
        tech_id = db.execute(
            "SELECT id FROM users WHERE username = 'tecnico1'"
        ).fetchone()["id"]
        cursor = db.execute(
            """
            INSERT INTO incidents
            (code, requester_id, location, category, description, impact,
             risk_people, priority, state, assigned_technician_id, created_at)
            VALUES ('INC-S04-PEND', ?, 'BIB-01', 'MOBILIARIO',
                    'Silla rota en zona de consulta', 'BAJO', 0, 'NORMAL',
                    'PENDIENTE_VALIDACION', ?, '2026-10-08T20:00:00+00:00')
            """,
            (req_id, tech_id),
        )
        incident_id = cursor.lastrowid
        db.execute(
            """
            INSERT INTO solutions (incident_id, technician_id, text, created_at)
            VALUES (?, ?, 'Se reemplazó la silla por una unidad en buen estado.',
                    '2026-10-08T21:00:00+00:00')
            """,
            (incident_id, tech_id),
        )
        db.execute(
            """
            INSERT INTO events
            (incident_id, actor_id, action, from_state, to_state, detail, created_at)
            VALUES (?, ?, 'SOLUCION_PROPUESTA', 'EN_ATENCION',
                    'PENDIENTE_VALIDACION',
                    'Se reemplazó la silla por una unidad en buen estado.',
                    '2026-10-08T21:00:00+00:00')
            """,
            (incident_id, tech_id),
        )
        db.commit()
        return incident_id, tech_id


def create_closed_incident(app, *, closed_at, requester="solicitante1"):
    with app.app_context():
        db = get_db()
        req_id = db.execute(
            "SELECT id FROM users WHERE username = ?", (requester,)
        ).fetchone()["id"]
        tech_id = db.execute(
            "SELECT id FROM users WHERE username = 'tecnico1'"
        ).fetchone()["id"]
        cursor = db.execute(
            """
            INSERT INTO incidents
            (code, requester_id, location, category, description, impact,
             risk_people, priority, state, assigned_technician_id, created_at, closed_at)
            VALUES ('INC-S04-CLOSE', ?, 'LAB-01', 'TIC',
                    'Equipo de red sin conectividad estable', 'ALTO', 0, 'ALTA',
                    'CERRADA', ?, '2026-10-05T10:00:00+00:00', ?)
            """,
            (req_id, tech_id, closed_at),
        )
        incident_id = cursor.lastrowid
        db.execute(
            """
            INSERT INTO solutions (incident_id, technician_id, text, created_at)
            VALUES (?, ?, 'Se reinició el equipo y se verificó la conectividad.',
                    '2026-10-06T10:00:00+00:00')
            """,
            (incident_id, tech_id),
        )
        db.execute(
            """
            INSERT INTO events
            (incident_id, actor_id, action, from_state, to_state, detail, created_at)
            VALUES (?, ?, 'CIERRE_CONFIRMADO', 'PENDIENTE_VALIDACION',
                    'CERRADA', 'Cierre previo de prueba', ?)
            """,
            (incident_id, req_id, closed_at),
        )
        db.commit()
        return incident_id, tech_id


@pytest.mark.parametrize(
    ("value", "valid"),
    [
        ("x" * 9, False),
        ("x" * 10, True),
        ("x" * 300, True),
        ("x" * 301, False),
    ],
)
def test_s04_reason_limits(value, valid):
    _cleaned, error = validate_reason(value)
    assert (error is None) is valid


@pytest.mark.integration
def test_s04_owner_confirms_pending_solution_and_closes(app, client):
    incident_id, _tech_id = create_pending_incident(app)
    fixed_now = datetime(2026, 10, 9, 1, 0, tzinfo=timezone.utc)
    app.config["NOW_PROVIDER"] = lambda: fixed_now

    login(client, username="solicitante1")
    response = client.post(f"/incidents/{incident_id}/confirm")

    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        incident = db.execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        event = db.execute(
            """
            SELECT * FROM events
            WHERE incident_id = ? AND action = 'CIERRE_CONFIRMADO'
            ORDER BY id DESC
            """,
            (incident_id,),
        ).fetchone()

        assert incident["state"] == "CERRADA"
        assert incident["closed_at"] == fixed_now.isoformat(timespec="seconds")
        assert event["to_state"] == "CERRADA"


@pytest.mark.integration
def test_s04_other_requester_cannot_confirm(app, client):
    incident_id, _tech_id = create_pending_incident(app, requester="solicitante1")

    login(client, username="solicitante2")
    response = client.post(f"/incidents/{incident_id}/confirm")

    assert response.status_code == 403

    with app.app_context():
        incident = get_db().execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        assert incident["state"] == "PENDIENTE_VALIDACION"


@pytest.mark.integration
def test_s04_rejection_returns_to_attention_and_preserves_technician_and_solution(app, client):
    incident_id, original_tech = create_pending_incident(app)
    reason = "El daño sigue presente después de la reparación"

    login(client, username="solicitante1")
    response = client.post(
        f"/incidents/{incident_id}/reject",
        data={"reason": reason},
    )

    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        incident = db.execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        solution = db.execute(
            "SELECT * FROM solutions WHERE incident_id = ?", (incident_id,)
        ).fetchone()
        event = db.execute(
            """
            SELECT * FROM events
            WHERE incident_id = ? AND action = 'SOLUCION_RECHAZADA'
            """,
            (incident_id,),
        ).fetchone()

        assert incident["state"] == "EN_ATENCION"
        assert incident["assigned_technician_id"] == original_tech
        assert solution is not None
        assert event["detail"] == reason


@pytest.mark.integration
def test_s04_invalid_rejection_reason_has_no_effect(app, client):
    incident_id, _tech_id = create_pending_incident(app)

    login(client, username="solicitante1")
    response = client.post(
        f"/incidents/{incident_id}/reject",
        data={"reason": "corto"},
    )

    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        incident = db.execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        rejected = db.execute(
            """
            SELECT COUNT(*) FROM events
            WHERE incident_id = ? AND action = 'SOLUCION_RECHAZADA'
            """,
            (incident_id,),
        ).fetchone()[0]

        assert incident["state"] == "PENDIENTE_VALIDACION"
        assert rejected == 0


@pytest.mark.integration
def test_s04_reopen_exactly_48_hours_is_allowed(app, client):
    now = datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)
    closed_at = (now - timedelta(hours=48)).isoformat(timespec="seconds")
    incident_id, original_tech = create_closed_incident(app, closed_at=closed_at)
    app.config["NOW_PROVIDER"] = lambda: now

    login(client, username="solicitante1")
    response = client.post(
        f"/incidents/{incident_id}/reopen",
        data={"reason": "La falla volvió a aparecer durante la prueba"},
    )

    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        incident = db.execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        solutions = db.execute(
            "SELECT COUNT(*) FROM solutions WHERE incident_id = ?", (incident_id,)
        ).fetchone()[0]
        closes = db.execute(
            """
            SELECT COUNT(*) FROM events
            WHERE incident_id = ? AND action = 'CIERRE_CONFIRMADO'
            """,
            (incident_id,),
        ).fetchone()[0]
        reopen = db.execute(
            """
            SELECT * FROM events
            WHERE incident_id = ? AND action = 'REABIERTA'
            """,
            (incident_id,),
        ).fetchone()

        assert incident["state"] == "EN_ATENCION"
        assert incident["assigned_technician_id"] == original_tech
        assert solutions == 1
        assert closes == 1
        assert reopen is not None


@pytest.mark.integration
def test_s04_reopen_after_48_hours_is_rejected_without_changes(app, client):
    now = datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)
    closed_at = (now - timedelta(hours=48, seconds=1)).isoformat(timespec="seconds")
    incident_id, original_tech = create_closed_incident(app, closed_at=closed_at)
    app.config["NOW_PROVIDER"] = lambda: now

    login(client, username="solicitante1")
    response = client.post(
        f"/incidents/{incident_id}/reopen",
        data={"reason": "La falla volvió a aparecer durante la prueba"},
    )

    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        incident = db.execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        reopened = db.execute(
            """
            SELECT COUNT(*) FROM events
            WHERE incident_id = ? AND action = 'REABIERTA'
            """,
            (incident_id,),
        ).fetchone()[0]

        assert incident["state"] == "CERRADA"
        assert incident["assigned_technician_id"] == original_tech
        assert reopened == 0


@pytest.mark.integration
def test_s04_coordinator_cannot_confirm_or_reopen_for_requester(app, client):
    pending_id, _ = create_pending_incident(app)
    now = datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)
    closed_id, _ = create_closed_incident(
        app,
        closed_at=(now - timedelta(hours=2)).isoformat(timespec="seconds"),
    )
    app.config["NOW_PROVIDER"] = lambda: now

    login(client, username="coordinador")

    confirm = client.post(f"/incidents/{pending_id}/confirm")
    reopen = client.post(
        f"/incidents/{closed_id}/reopen",
        data={"reason": "Motivo válido para intentar reapertura"},
    )

    assert confirm.status_code == 403
    assert reopen.status_code == 403
