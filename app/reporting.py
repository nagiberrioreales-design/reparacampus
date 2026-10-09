from flask import Blueprint, abort, g, render_template, request

from .auth import login_required
from .db import get_db


bp = Blueprint("reporting", __name__, url_prefix="/reports")

VALID_STATES = {
    "REGISTRADA",
    "ASIGNADA",
    "EN_ATENCION",
    "PENDIENTE_VALIDACION",
    "CERRADA",
}
VALID_PRIORITIES = {"NORMAL", "ALTA", "CRITICA"}


def _authorized_incident(incident_id):
    incident = get_db().execute(
        """
        SELECT i.*, r.display_name AS requester_name,
               t.display_name AS technician_name
        FROM incidents i
        JOIN users r ON r.id = i.requester_id
        LEFT JOIN users t ON t.id = i.assigned_technician_id
        WHERE i.id = ?
        """,
        (incident_id,),
    ).fetchone()

    if incident is None:
        abort(404)

    role = g.user["role"]
    allowed = (
        role == "COORDINADOR"
        or (role == "SOLICITANTE" and incident["requester_id"] == g.user["id"])
        or (role == "TECNICO" and incident["assigned_technician_id"] == g.user["id"])
    )
    if not allowed:
        abort(403)

    return incident


def _dashboard(db):
    by_state = {
        row["state"]: row["total"]
        for row in db.execute(
            "SELECT state, COUNT(*) AS total FROM incidents GROUP BY state"
        ).fetchall()
    }
    by_priority = {
        row["priority"]: row["total"]
        for row in db.execute(
            """
            SELECT priority, COUNT(*) AS total
            FROM incidents
            WHERE priority IS NOT NULL
            GROUP BY priority
            """
        ).fetchall()
    }
    total = db.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
    closed = db.execute(
        "SELECT COUNT(*) FROM incidents WHERE state = 'CERRADA'"
    ).fetchone()[0]
    open_critical = db.execute(
        """
        SELECT COUNT(*) FROM incidents
        WHERE priority = 'CRITICA' AND state <> 'CERRADA'
        """
    ).fetchone()[0]

    percentage = 0.0 if total == 0 else (closed / total) * 100
    return {
        "by_state": by_state,
        "by_priority": by_priority,
        "total": total,
        "closed": closed,
        "open_critical": open_critical,
        "close_percentage": f"{percentage:.1f}".replace(".", ",") + " %",
    }


@bp.route("/incidents")
@login_required
def list_incidents():
    state = request.args.get("state", "").strip()
    priority = request.args.get("priority", "").strip()

    if state and state not in VALID_STATES:
        abort(400)
    if priority and priority not in VALID_PRIORITIES:
        abort(400)

    conditions = []
    params = []

    if g.user["role"] == "SOLICITANTE":
        conditions.append("i.requester_id = ?")
        params.append(g.user["id"])
    elif g.user["role"] == "TECNICO":
        conditions.append("i.assigned_technician_id = ?")
        params.append(g.user["id"])
    elif g.user["role"] != "COORDINADOR":
        abort(403)

    if state:
        conditions.append("i.state = ?")
        params.append(state)

    if priority:
        conditions.append("i.priority = ?")
        params.append(priority)

    where = " WHERE " + " AND ".join(conditions) if conditions else ""

    incidents = get_db().execute(
        f"""
        SELECT i.*, r.display_name AS requester_name,
               t.display_name AS technician_name
        FROM incidents i
        JOIN users r ON r.id = i.requester_id
        LEFT JOIN users t ON t.id = i.assigned_technician_id
        {where}
        ORDER BY i.id DESC
        """,
        params,
    ).fetchall()

    dashboard = _dashboard(get_db()) if g.user["role"] == "COORDINADOR" else None

    return render_template(
        "reports/incidents.html",
        incidents=incidents,
        dashboard=dashboard,
        selected_state=state,
        selected_priority=priority,
        states=sorted(VALID_STATES),
        priorities=["CRITICA", "ALTA", "NORMAL"],
    )


@bp.route("/incidents/<int:incident_id>/history")
@login_required
def history(incident_id):
    incident = _authorized_incident(incident_id)
    db = get_db()

    events = db.execute(
        """
        SELECT e.*, u.display_name AS actor_name
        FROM events e
        JOIN users u ON u.id = e.actor_id
        WHERE e.incident_id = ?
        ORDER BY e.id ASC
        """,
        (incident_id,),
    ).fetchall()

    solutions = db.execute(
        """
        SELECT s.*, u.display_name AS technician_name
        FROM solutions s
        JOIN users u ON u.id = s.technician_id
        WHERE s.incident_id = ?
        ORDER BY s.id ASC
        """,
        (incident_id,),
    ).fetchall()

    return render_template(
        "reports/history.html",
        incident=incident,
        events=events,
        solutions=solutions,
    )
