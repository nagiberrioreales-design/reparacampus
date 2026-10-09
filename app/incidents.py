from datetime import datetime, timezone
from uuid import uuid4

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from .auth import role_required
from .db import get_db
from .domain import calculate_priority, validate_new_incident


bp = Blueprint("incidents", __name__, url_prefix="/incidents")


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def generate_incident_code():
    return f"INC-{uuid4().hex[:8].upper()}"


@bp.route("/")
@role_required("SOLICITANTE")
def index():
    incidents = get_db().execute(
        """
        SELECT id, code, location, category, description, impact, risk_people, state, created_at
        FROM incidents
        WHERE requester_id = ?
        ORDER BY id DESC
        """,
        (g.user["id"],),
    ).fetchall()
    return render_template("incidents/index.html", incidents=incidents)


@bp.route("/new", methods=("GET", "POST"))
@role_required("SOLICITANTE")
def create():
    errors = {}
    values = {}

    if request.method == "POST":
        values = request.form.to_dict()
        cleaned, errors = validate_new_incident(values)

        if not errors:
            db = get_db()
            code = generate_incident_code()
            created_at = utc_now_iso()

            with db:
                cursor = db.execute(
                    """
                    INSERT INTO incidents
                    (code, requester_id, location, category, description, impact, risk_people, state, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'REGISTRADA', ?)
                    """,
                    (
                        code,
                        g.user["id"],
                        cleaned["location"],
                        cleaned["category"],
                        cleaned["description"],
                        cleaned["impact"],
                        int(cleaned["risk_people"]),
                        created_at,
                    ),
                )
                incident_id = cursor.lastrowid
                db.execute(
                    """
                    INSERT INTO events
                    (incident_id, actor_id, action, from_state, to_state, detail, created_at)
                    VALUES (?, ?, 'CREADA', NULL, 'REGISTRADA', NULL, ?)
                    """,
                    (incident_id, g.user["id"], created_at),
                )

            flash(f"Incidencia {code} registrada correctamente.", "success")
            return redirect(url_for("incidents.index"))

    return render_template("incidents/new.html", errors=errors, values=values)


@bp.route("/manage")
@role_required("COORDINADOR")
def manage():
    db = get_db()
    incidents = db.execute(
        """
        SELECT i.*, u.display_name AS requester_name,
               t.display_name AS technician_name
        FROM incidents i
        JOIN users u ON u.id = i.requester_id
        LEFT JOIN users t ON t.id = i.assigned_technician_id
        ORDER BY i.id DESC
        """
    ).fetchall()
    technicians = db.execute(
        """
        SELECT id, display_name
        FROM users
        WHERE role = 'TECNICO' AND active = 1
        ORDER BY display_name
        """
    ).fetchall()
    return render_template(
        "incidents/manage.html",
        incidents=incidents,
        technicians=technicians,
    )


@bp.post("/<int:incident_id>/assign")
@role_required("COORDINADOR")
def assign(incident_id):
    db = get_db()
    incident = db.execute(
        "SELECT * FROM incidents WHERE id = ?",
        (incident_id,),
    ).fetchone()

    if incident is None:
        abort(404)

    if incident["state"] != "REGISTRADA" or incident["assigned_technician_id"] is not None:
        flash("La incidencia ya fue asignada o está en un estado que no permite asignación.", "error")
        return redirect(url_for("incidents.manage"))

    technician_id_raw = request.form.get("technician_id", "").strip()
    try:
        technician_id = int(technician_id_raw)
    except (TypeError, ValueError):
        flash("Selecciona un técnico válido.", "error")
        return redirect(url_for("incidents.manage"))

    technician = db.execute(
        """
        SELECT id, display_name
        FROM users
        WHERE id = ? AND role = 'TECNICO' AND active = 1
        """,
        (technician_id,),
    ).fetchone()

    if technician is None:
        flash("El técnico seleccionado no existe o no está activo.", "error")
        return redirect(url_for("incidents.manage"))

    priority = calculate_priority(incident["risk_people"], incident["impact"])
    changed_at = utc_now_iso()

    with db:
        update = db.execute(
            """
            UPDATE incidents
            SET priority = ?, assigned_technician_id = ?, state = 'ASIGNADA'
            WHERE id = ? AND state = 'REGISTRADA' AND assigned_technician_id IS NULL
            """,
            (priority, technician_id, incident_id),
        )

        if update.rowcount != 1:
            raise RuntimeError("La incidencia cambió antes de completar la asignación.")

        db.execute(
            """
            INSERT INTO events
            (incident_id, actor_id, action, from_state, to_state, detail, created_at)
            VALUES (?, ?, 'ASIGNADA', 'REGISTRADA', 'ASIGNADA', ?, ?)
            """,
            (
                incident_id,
                g.user["id"],
                f"Técnico: {technician['display_name']}; prioridad: {priority}",
                changed_at,
            ),
        )

    flash(
        f"{incident['code']} asignada a {technician['display_name']} con prioridad {priority}.",
        "success",
    )
    return redirect(url_for("incidents.manage"))
