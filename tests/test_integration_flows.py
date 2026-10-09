import pytest

from app.db import get_db
from tests.conftest import login


VALID_FORM = {
    "location": "LAB-01",
    "category": "TIC",
    "description": "Punto de red sin conexión durante la clase",
    "impact": "ALTO",
    "risk_people": "false",
}


def logout(client):
    return client.post("/auth/logout", follow_redirects=False)


def user_id(app, username):
    with app.app_context():
        return get_db().execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()["id"]


def latest_incident_id(app):
    with app.app_context():
        return get_db().execute(
            "SELECT id FROM incidents ORDER BY id DESC LIMIT 1"
        ).fetchone()["id"]


def create_and_assign(app, client):
    login(client, username="solicitante1")
    response = client.post("/incidents/new", data=VALID_FORM)
    assert response.status_code == 302
    incident_id = latest_incident_id(app)
    logout(client)

    login(client, username="coordinador")
    response = client.post(
        f"/incidents/{incident_id}/assign",
        data={"technician_id": str(user_id(app, "tecnico1"))},
    )
    assert response.status_code == 302
    logout(client)
    return incident_id


def start_and_propose(client, incident_id, solution):
    login(client, username="tecnico1")
    start = client.post(f"/incidents/{incident_id}/start")
    assert start.status_code == 302
    propose = client.post(
        f"/incidents/{incident_id}/solution",
        data={"solution": solution},
    )
    assert propose.status_code == 302
    logout(client)


@pytest.mark.integration
def test_full_flow_register_assign_start_propose_confirm(app, client):
    incident_id = create_and_assign(app, client)
    start_and_propose(
        client,
        incident_id,
        "Se cambió el conector y se verificó la conexión del punto de red.",
    )

    login(client, username="solicitante1")
    confirm = client.post(f"/incidents/{incident_id}/confirm")
    assert confirm.status_code == 302

    with app.app_context():
        db = get_db()
        incident = db.execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        actions = [
            row["action"]
            for row in db.execute(
                "SELECT action FROM events WHERE incident_id = ? ORDER BY id",
                (incident_id,),
            ).fetchall()
        ]

        assert incident["state"] == "CERRADA"
        assert actions == [
            "CREADA",
            "ASIGNADA",
            "INICIO_ATENCION",
            "SOLUCION_PROPUESTA",
            "CIERRE_CONFIRMADO",
        ]


@pytest.mark.integration
def test_flow_rejects_solution_and_accepts_new_solution(app, client):
    incident_id = create_and_assign(app, client)
    start_and_propose(
        client,
        incident_id,
        "Se reinició el punto de acceso y se dejó funcionando temporalmente.",
    )

    login(client, username="solicitante1")
    reject = client.post(
        f"/incidents/{incident_id}/reject",
        data={"reason": "La conexión volvió a fallar después de unos minutos"},
    )
    assert reject.status_code == 302
    logout(client)

    login(client, username="tecnico1")
    second_solution = client.post(
        f"/incidents/{incident_id}/solution",
        data={"solution": "Se reemplazó el cable dañado y se repitieron las pruebas de conexión."},
    )
    assert second_solution.status_code == 302
    logout(client)

    login(client, username="solicitante1")
    confirm = client.post(f"/incidents/{incident_id}/confirm")
    assert confirm.status_code == 302

    with app.app_context():
        db = get_db()
        incident = db.execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        solution_count = db.execute(
            "SELECT COUNT(*) FROM solutions WHERE incident_id = ?", (incident_id,)
        ).fetchone()[0]
        rejection_count = db.execute(
            """
            SELECT COUNT(*) FROM events
            WHERE incident_id = ? AND action = 'SOLUCION_RECHAZADA'
            """,
            (incident_id,),
        ).fetchone()[0]

        assert incident["state"] == "CERRADA"
        assert solution_count == 2
        assert rejection_count == 1


@pytest.mark.integration
def test_flow_close_reopen_new_solution_and_close_again(app, client):
    incident_id = create_and_assign(app, client)
    start_and_propose(
        client,
        incident_id,
        "Se ajustó el cableado y la conexión quedó estable en la primera prueba.",
    )

    login(client, username="solicitante1")
    first_close = client.post(f"/incidents/{incident_id}/confirm")
    assert first_close.status_code == 302

    reopen = client.post(
        f"/incidents/{incident_id}/reopen",
        data={"reason": "El problema volvió a presentarse durante la misma jornada"},
    )
    assert reopen.status_code == 302
    logout(client)

    login(client, username="tecnico1")
    new_solution = client.post(
        f"/incidents/{incident_id}/solution",
        data={"solution": "Se reemplazó el conector completo y se verificó con varias pruebas."},
    )
    assert new_solution.status_code == 302
    logout(client)

    login(client, username="solicitante1")
    second_close = client.post(f"/incidents/{incident_id}/confirm")
    assert second_close.status_code == 302

    with app.app_context():
        db = get_db()
        incident = db.execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        closes = db.execute(
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
        solutions = db.execute(
            "SELECT COUNT(*) FROM solutions WHERE incident_id = ?", (incident_id,)
        ).fetchone()[0]

        assert incident["state"] == "CERRADA"
        assert closes == 2
        assert reopens == 1
        assert solutions == 2
