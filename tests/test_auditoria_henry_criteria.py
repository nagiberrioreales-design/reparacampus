"""Pruebas complementarias de trazabilidad AC-S03-07, S04-08/09 y S05-04/06.

Estas verificaciones fueron preparadas con asistencia de IA. La aprobación
humana independiente y la revisión exhaustiva de la matriz son pasos separados.
"""
import re
from datetime import datetime, timedelta, timezone

import pytest

from app.db import get_db
from app.reporting import _dashboard
from tests.conftest import login
from tests.test_integration_flows import create_and_assign, logout, start_and_propose, user_id
from tests.test_s03_attention_solution import create_assigned_incident
from tests.test_s04_validation_reopen import create_closed_incident, create_pending_incident
from tests.test_s05_query_history import add_incident


def _snapshot(app, incident_id):
    """Estado completo persistido, incluidos eventos y soluciones de una incidencia."""
    with app.app_context():
        db = get_db()
        incident = tuple(
            db.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
        )
        events = [
            tuple(row) for row in db.execute(
                "SELECT * FROM events WHERE incident_id = ? ORDER BY id", (incident_id,)
            ).fetchall()
        ]
        solutions = [
            tuple(row) for row in db.execute(
                "SELECT * FROM solutions WHERE incident_id = ? ORDER BY id", (incident_id,)
            ).fetchall()
        ]
        return incident, events, solutions


@pytest.mark.integration
def test_ac_s03_07_solution_before_attention_preserves_all_persisted_data(app, client):
    incident_id = create_assigned_incident(app, state="ASIGNADA")
    before = _snapshot(app, incident_id)

    login(client, username="tecnico1")
    response = client.post(
        f"/incidents/{incident_id}/solution",
        data={"solution": "Solución válida en longitud, pero enviada antes de iniciar."},
    )

    assert response.status_code == 302
    assert _snapshot(app, incident_id) == before
    assert len(before[1]) == 1
    assert len(before[2]) == 0


@pytest.mark.integration
def test_ac_s04_08_and_s05_04_complete_history_in_chronological_order(app, client):
    """Rechazo, dos cierres, reapertura y tres soluciones sin perder historial."""
    clock = {"now": datetime(2026, 10, 12, 9, 0, tzinfo=timezone.utc)}
    app.config["NOW_PROVIDER"] = lambda: clock["now"]

    first_text = "Se reinició el punto de red, pero el servicio volvió a fallar."
    second_text = "Se reparó el cableado y se comprobó la conexión de red."
    third_text = "Se cambió el conector y se realizaron pruebas de estabilidad."

    incident_id = create_and_assign(app, client)
    clock["now"] += timedelta(minutes=1)
    start_and_propose(client, incident_id, first_text)

    clock["now"] += timedelta(minutes=1)
    login(client, username="solicitante1")
    assert client.post(
        f"/incidents/{incident_id}/reject",
        data={"reason": "La conexión volvió a fallar después de la primera reparación"},
    ).status_code == 302
    logout(client)

    clock["now"] += timedelta(minutes=1)
    login(client, username="tecnico1")
    assert client.post(
        f"/incidents/{incident_id}/solution",
        data={"solution": second_text},
    ).status_code == 302
    logout(client)

    clock["now"] += timedelta(minutes=1)
    login(client, username="solicitante1")
    assert client.post(f"/incidents/{incident_id}/confirm").status_code == 302

    clock["now"] += timedelta(minutes=1)
    assert client.post(
        f"/incidents/{incident_id}/reopen",
        data={"reason": "La conexión falló de nuevo después del cierre"},
    ).status_code == 302
    logout(client)

    clock["now"] += timedelta(minutes=1)
    login(client, username="tecnico1")
    assert client.post(
        f"/incidents/{incident_id}/solution",
        data={"solution": third_text},
    ).status_code == 302
    logout(client)

    clock["now"] += timedelta(minutes=1)
    login(client, username="solicitante1")
    assert client.post(f"/incidents/{incident_id}/confirm").status_code == 302

    expected_actions = [
        "CREADA", "ASIGNADA", "INICIO_ATENCION", "SOLUCION_PROPUESTA",
        "SOLUCION_RECHAZADA", "SOLUCION_PROPUESTA", "CIERRE_CONFIRMADO",
        "REABIERTA", "SOLUCION_PROPUESTA", "CIERRE_CONFIRMADO",
    ]
    expected_actors = [
        "solicitante1", "coordinador", "tecnico1", "tecnico1",
        "solicitante1", "tecnico1", "solicitante1", "solicitante1",
        "tecnico1", "solicitante1",
    ]

    with app.app_context():
        db = get_db()
        incident = db.execute(
            "SELECT state, closed_at FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        events = db.execute(
            "SELECT id, action, actor_id, created_at, from_state, to_state "
            "FROM events WHERE incident_id = ? ORDER BY id ASC", (incident_id,)
        ).fetchall()
        solutions = db.execute(
            "SELECT id, text, technician_id, created_at FROM solutions "
            "WHERE incident_id = ? ORDER BY id ASC", (incident_id,)
        ).fetchall()

        assert incident["state"] == "CERRADA"
        assert incident["closed_at"] == clock["now"].isoformat(timespec="seconds")
        assert [row["action"] for row in events] == expected_actions
        assert [row["actor_id"] for row in events] == [
            user_id(app, actor) for actor in expected_actors
        ]
        assert [row["created_at"] for row in events] == sorted(
            row["created_at"] for row in events
        )
        assert [row["text"] for row in solutions] == [
            first_text, second_text, third_text
        ]
        assert [row["created_at"] for row in solutions] == sorted(
            row["created_at"] for row in solutions
        )
        assert all(
            row["technician_id"] == user_id(app, "tecnico1") for row in solutions
        )
        assert [row["to_state"] for row in events[-4:]] == [
            "CERRADA", "EN_ATENCION", "PENDIENTE_VALIDACION", "CERRADA"
        ]

    response = client.get(f"/reports/incidents/{incident_id}/history")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    event_section, solution_section = html.split("<h2>Soluciones registradas</h2>", 1)
    position = 0
    for action in expected_actions:
        position = event_section.find(f"<td>{action}</td>", position)
        assert position >= 0, f"Falta o está desordenado el evento {action}"
        position += len(f"<td>{action}</td>")
    # La lista exacta de acciones se verificó arriba directamente en SQLite.
    # No contar todas las celdas <td>: "ASIGNADA" también aparece como estado.
    assert solution_section.index(first_text) < solution_section.index(second_text)
    assert solution_section.index(second_text) < solution_section.index(third_text)
    assert "La conexión falló de nuevo después del cierre" in event_section
    assert clock["now"].isoformat(timespec="seconds") in event_section


@pytest.mark.parametrize(
    ("state", "action", "reason", "expired"),
    [
        ("PENDIENTE_VALIDACION", "reopen", "La falla continúa y solicita reapertura", False),
        ("CERRADA", "confirm", None, False),
        ("CERRADA", "reject", "La reparación sigue siendo insuficiente", False),
        ("PENDIENTE_VALIDACION", "reject", "corto", False),
        ("CERRADA", "reopen", "corto", False),
        ("CERRADA", "reopen", "El problema apareció nuevamente después del cierre", True),
    ],
)
@pytest.mark.integration
def test_ac_s04_09_invalid_actions_have_no_partial_effects(
    app, client, state, action, reason, expired
):
    now = datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc)
    app.config["NOW_PROVIDER"] = lambda: now
    if state == "CERRADA":
        closed_at = (now - timedelta(hours=49 if expired else 1)).isoformat(
            timespec="seconds"
        )
        incident_id, _ = create_closed_incident(app, closed_at=closed_at)
    else:
        incident_id, _ = create_pending_incident(app)

    before = _snapshot(app, incident_id)
    login(client, username="solicitante1")
    response = client.post(
        f"/incidents/{incident_id}/{action}",
        data={} if reason is None else {"reason": reason},
    )

    assert response.status_code == 302
    assert _snapshot(app, incident_id) == before


@pytest.mark.integration
def test_ac_s05_06_dashboard_exact_state_priority_and_open_critical_counts(app, client):
    rows = [
        ("AUD-01", "CERRADA", "ALTA"),
        ("AUD-02", "CERRADA", "CRITICA"),
        ("AUD-03", "EN_ATENCION", "CRITICA"),
        ("AUD-04", "ASIGNADA", "NORMAL"),
        ("AUD-05", "PENDIENTE_VALIDACION", "CRITICA"),
        ("AUD-06", "REGISTRADA", None),
        ("AUD-07", "REGISTRADA", "NORMAL"),
    ]
    for code, state, priority in rows:
        add_incident(
            app, code=code, requester="solicitante1",
            technician="tecnico1" if state != "REGISTRADA" else None,
            state=state, priority=priority,
        )

    with app.app_context():
        dashboard = _dashboard(get_db())
    assert dashboard == {
        "by_state": {
            "REGISTRADA": 2, "ASIGNADA": 1, "EN_ATENCION": 1,
            "PENDIENTE_VALIDACION": 1, "CERRADA": 2,
        },
        "by_priority": {"NORMAL": 2, "ALTA": 1, "CRITICA": 3},
        "total": 7,
        "closed": 2,
        "open_critical": 2,
        "close_percentage": "28,6 %",
    }

    
    login(client, username="coordinador")
    response = client.get("/reports/incidents")
    assert response.status_code == 200

    html = response.get_data(as_text=True)
    assert "28,6 %" in html

    # Comprobar las incidencias críticas no cerradas.
    assert re.search(
        r"<span>\s*Críticas no cerradas\s*</span>\s*<strong>\s*2\s*</strong>",
        html,
    )

    # Comprobar los conteos por estado.
    for state, count in dashboard["by_state"].items():
        label = state.replace("_", " ")
        assert re.search(
            rf"<p>\s*{re.escape(label)}:\s*{count}\s*</p>",
            html,
        )

    # Comprobar los conteos por prioridad.
    for priority, count in dashboard["by_priority"].items():
        assert re.search(
            rf"<p>\s*{re.escape(priority)}:\s*{count}\s*</p>",
            html,
        )
