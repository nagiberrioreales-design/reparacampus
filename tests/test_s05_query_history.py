import pytest

from app.db import get_db
from tests.conftest import login


def ids(app):
    with app.app_context():
        db = get_db()
        rows = db.execute("SELECT id, username FROM users").fetchall()
        return {row["username"]: row["id"] for row in rows}


def add_incident(
    app,
    *,
    code,
    requester,
    technician=None,
    state="REGISTRADA",
    priority=None,
    detail=None,
    solution=None,
):
    user_ids = ids(app)
    with app.app_context():
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO incidents
            (code, requester_id, location, category, description, impact,
             risk_people, priority, state, assigned_technician_id, created_at)
            VALUES (?, ?, 'LAB-01', 'TIC',
                    'Incidencia creada para pruebas de consulta',
                    'ALTO', 0, ?, ?, ?, '2026-10-08T20:00:00+00:00')
            """,
            (
                code,
                user_ids[requester],
                priority,
                state,
                user_ids[technician] if technician else None,
            ),
        )
        incident_id = cursor.lastrowid
        db.execute(
            """
            INSERT INTO events
            (incident_id, actor_id, action, from_state, to_state, detail, created_at)
            VALUES (?, ?, 'CREADA', NULL, 'REGISTRADA', ?, '2026-10-08T20:00:00+00:00')
            """,
            (incident_id, user_ids[requester], detail),
        )
        if solution and technician:
            db.execute(
                """
                INSERT INTO solutions (incident_id, technician_id, text, created_at)
                VALUES (?, ?, ?, '2026-10-08T21:00:00+00:00')
                """,
                (incident_id, user_ids[technician], solution),
            )
            db.execute(
                """
                INSERT INTO events
                (incident_id, actor_id, action, from_state, to_state, detail, created_at)
                VALUES (?, ?, 'SOLUCION_PROPUESTA', 'EN_ATENCION',
                        'PENDIENTE_VALIDACION', ?,
                        '2026-10-08T21:00:00+00:00')
                """,
                (incident_id, user_ids[technician], solution),
            )
        db.commit()
        return incident_id


@pytest.mark.integration
def test_s05_requester_only_sees_own_incidents(app, client):
    add_incident(app, code="INC-OWN", requester="solicitante1")
    add_incident(app, code="INC-OTHER", requester="solicitante2")

    login(client, username="solicitante1")
    response = client.get("/reports/incidents")

    assert response.status_code == 200
    assert b"INC-OWN" in response.data
    assert b"INC-OTHER" not in response.data


@pytest.mark.integration
def test_s05_technician_only_sees_assigned_incidents(app, client):
    add_incident(
        app,
        code="INC-T1",
        requester="solicitante1",
        technician="tecnico1",
        state="ASIGNADA",
        priority="ALTA",
    )
    add_incident(
        app,
        code="INC-T2",
        requester="solicitante2",
        technician="tecnico2",
        state="ASIGNADA",
        priority="NORMAL",
    )

    login(client, username="tecnico1")
    response = client.get("/reports/incidents")

    assert response.status_code == 200
    assert b"INC-T1" in response.data
    assert b"INC-T2" not in response.data


@pytest.mark.integration
def test_s05_coordinator_combines_state_and_priority_filters(app, client):
    add_incident(
        app,
        code="INC-MATCH",
        requester="solicitante1",
        technician="tecnico1",
        state="CERRADA",
        priority="ALTA",
    )
    add_incident(
        app,
        code="INC-WRONG-STATE",
        requester="solicitante1",
        technician="tecnico1",
        state="EN_ATENCION",
        priority="ALTA",
    )
    add_incident(
        app,
        code="INC-WRONG-PRIORITY",
        requester="solicitante2",
        technician="tecnico2",
        state="CERRADA",
        priority="NORMAL",
    )

    login(client, username="coordinador")
    response = client.get("/reports/incidents?state=CERRADA&priority=ALTA")

    assert response.status_code == 200
    assert b"INC-MATCH" in response.data
    assert b"INC-WRONG-STATE" not in response.data
    assert b"INC-WRONG-PRIORITY" not in response.data


@pytest.mark.integration
def test_s05_direct_history_access_respects_permissions(app, client):
    incident_id = add_incident(
        app,
        code="INC-PRIVATE",
        requester="solicitante2",
        technician="tecnico2",
        state="EN_ATENCION",
        priority="NORMAL",
    )

    login(client, username="solicitante1")
    response = client.get(f"/reports/incidents/{incident_id}/history")

    assert response.status_code == 403


@pytest.mark.integration
def test_s05_history_contains_events_solutions_and_escapes_text(app, client):
    incident_id = add_incident(
        app,
        code="INC-HISTORY",
        requester="solicitante1",
        technician="tecnico1",
        state="PENDIENTE_VALIDACION",
        priority="CRITICA",
        detail="<script>alert('x')</script>",
        solution="Se ajustó el cableado y se probó el equipo correctamente.",
    )

    login(client, username="solicitante1")
    response = client.get(f"/reports/incidents/{incident_id}/history")

    assert response.status_code == 200
    assert b"SOLUCION_PROPUESTA" in response.data
    assert b"Se ajust" in response.data
    assert b"<script>" not in response.data
    assert b"&lt;script&gt;" in response.data


@pytest.mark.integration
def test_s05_history_has_no_edit_operation(app, client):
    incident_id = add_incident(
        app,
        code="INC-IMMUTABLE",
        requester="solicitante1",
    )

    login(client, username="solicitante1")
    response = client.post(
        f"/reports/incidents/{incident_id}/history",
        data={"detail": "intento de edición"},
    )

    assert response.status_code == 405


@pytest.mark.integration
def test_s05_dashboard_zero_records_is_zero_percent(app, client):
    login(client, username="coordinador")
    response = client.get("/reports/incidents")

    assert response.status_code == 200
    assert "0,0 %".encode() in response.data


@pytest.mark.integration
def test_s05_dashboard_counts_and_close_percentage(app, client):
    add_incident(
        app,
        code="INC-D1",
        requester="solicitante1",
        technician="tecnico1",
        state="CERRADA",
        priority="ALTA",
    )
    add_incident(
        app,
        code="INC-D2",
        requester="solicitante1",
        technician="tecnico1",
        state="EN_ATENCION",
        priority="CRITICA",
    )
    add_incident(
        app,
        code="INC-D3",
        requester="solicitante2",
        technician="tecnico2",
        state="ASIGNADA",
        priority="NORMAL",
    )
    add_incident(
        app,
        code="INC-D4",
        requester="solicitante2",
        technician="tecnico2",
        state="PENDIENTE_VALIDACION",
        priority="CRITICA",
    )

    login(client, username="coordinador")
    response = client.get("/reports/incidents")

    assert response.status_code == 200
    assert "25,0 %".encode() in response.data
    assert b"Cr" in response.data
    assert b"2" in response.data


@pytest.mark.integration
def test_s05_reopening_reduces_close_percentage_and_keeps_previous_closure(app, client):
    from datetime import datetime, timedelta, timezone

    user_ids = ids(app)
    now = datetime(2026, 10, 9, 5, 30, tzinfo=timezone.utc)
    closed_at = (now - timedelta(hours=1)).isoformat(timespec="seconds")
    app.config["NOW_PROVIDER"] = lambda: now

    with app.app_context():
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO incidents
            (code, requester_id, location, category, description, impact,
             risk_people, priority, state, assigned_technician_id, created_at, closed_at)
            VALUES ('INC-REOPEN-METRIC', ?, 'LAB-01', 'TIC',
                    'Incidencia cerrada usada para comprobar el porcentaje',
                    'ALTO', 0, 'ALTA', 'CERRADA', ?,
                    '2026-10-09T03:00:00+00:00', ?)
            """,
            (user_ids["solicitante1"], user_ids["tecnico1"], closed_at),
        )
        incident_id = cursor.lastrowid
        db.execute(
            """
            INSERT INTO events
            (incident_id, actor_id, action, from_state, to_state, detail, created_at)
            VALUES (?, ?, 'CIERRE_CONFIRMADO', 'PENDIENTE_VALIDACION',
                    'CERRADA', 'Cierre previo conservado', ?)
            """,
            (incident_id, user_ids["solicitante1"], closed_at),
        )
        db.commit()

    login(client, username="coordinador")
    before = client.get("/reports/incidents")
    assert "100,0 %".encode() in before.data
    client.post("/auth/logout")
    login(client, username="solicitante1")
    reopened = client.post(
        f"/incidents/{incident_id}/reopen",
        data={"reason": "La incidencia volvió a presentarse durante la prueba"},
    )
    assert reopened.status_code == 302
    client.post("/auth/logout")
    login(client, username="coordinador")
    after = client.get("/reports/incidents")
    assert "0,0 %".encode() in after.data

    with app.app_context():
        db = get_db()
        prior_closures = db.execute(
            """
            SELECT COUNT(*) FROM events
            WHERE incident_id = ? AND action = 'CIERRE_CONFIRMADO'
            """,
            (incident_id,),
        ).fetchone()[0]
        reopens = db.execute(
            """
            SELECT COUNT(*) FROM events
            WHERE incident_id = ? AND action = 'REABIERTA'
            """,
            (incident_id,),
        ).fetchone()[0]

        assert prior_closures == 1
        assert reopens == 1
