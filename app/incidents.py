from datetime import datetime, timedelta, timezone
from uuid import uuid4

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from .auth import role_required
from .db import get_db
from .domain import (
    calculate_priority,
    validate_new_incident,
    validate_reason,
    validate_solution,
)


bp = Blueprint("incidents", __name__, url_prefix="/incidents")


def current_utc():
    provider = current_app.config.get("NOW_PROVIDER")
    now = provider() if provider else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


def utc_now_iso():
    return current_utc().isoformat(timespec="seconds")


def generate_incident_code():
    return f"INC-{uuid4().hex[:8].upper()}"


def get_owned_incident(incident_id):
    incident = get_db().execute(
        "SELECT * FROM incidents WHERE id = ?",
        (incident_id,),
    ).fetchone()
    if incident is None:
        abort(404)
    if incident["requester_id"] != g.user["id"]:
        abort(403)
    return incident


@bp.route("/")
@role_required("SOLICITANTE")
def index():
    incidents = get_db().execute(
        """
        SELECT i.*,
               (
                   SELECT s.text
                   FROM solutions s
                   WHERE s.incident_id = i.id
                   ORDER BY s.id DESC
                   LIMIT 1
               ) AS latest_solution
        FROM incidents i
        WHERE i.requester_id = ?
        ORDER BY i.id DESC
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


@bp.route("/assigned")
@role_required("TECNICO")
def assigned():
    incidents = get_db().execute(
        """
        SELECT i.*, u.display_name AS requester_name
        FROM incidents i
        JOIN users u ON u.id = i.requester_id
        WHERE i.assigned_technician_id = ?
        ORDER BY i.id DESC
        """,
        (g.user["id"],),
    ).fetchall()
    return render_template("incidents/assigned.html", incidents=incidents)


@bp.post("/<int:incident_id>/start")
@role_required("TECNICO")
def start_attention(incident_id):
    db = get_db()
    incident = db.execute(
        "SELECT * FROM incidents WHERE id = ?",
        (incident_id,),
    ).fetchone()

    if incident is None:
        abort(404)

    if incident["assigned_technician_id"] != g.user["id"]:
        abort(403)

    if incident["state"] != "ASIGNADA":
        flash("La incidencia no está en estado ASIGNADA.", "error")
        return redirect(url_for("incidents.assigned"))

    changed_at = utc_now_iso()

    with db:
        update = db.execute(
            """
            UPDATE incidents
            SET state = 'EN_ATENCION'
            WHERE id = ? AND state = 'ASIGNADA' AND assigned_technician_id = ?
            """,
            (incident_id, g.user["id"]),
        )
        if update.rowcount != 1:
            raise RuntimeError("La incidencia cambió antes de iniciar la atención.")

        db.execute(
            """
            INSERT INTO events
            (incident_id, actor_id, action, from_state, to_state, detail, created_at)
            VALUES (?, ?, 'INICIO_ATENCION', 'ASIGNADA', 'EN_ATENCION', NULL, ?)
            """,
            (incident_id, g.user["id"], changed_at),
        )

    flash(f"{incident['code']} ahora está EN_ATENCION.", "success")
    return redirect(url_for("incidents.assigned"))


@bp.post("/<int:incident_id>/solution")
@role_required("TECNICO")
def propose_solution(incident_id):
    db = get_db()
    incident = db.execute(
        "SELECT * FROM incidents WHERE id = ?",
        (incident_id,),
    ).fetchone()

    if incident is None:
        abort(404)

    if incident["assigned_technician_id"] != g.user["id"]:
        abort(403)

    if incident["state"] != "EN_ATENCION":
        flash("La incidencia debe estar EN_ATENCION antes de registrar una solución.", "error")
        return redirect(url_for("incidents.assigned"))

    solution_text, error = validate_solution(request.form.get("solution", ""))
    if error:
        flash(error, "error")
        return redirect(url_for("incidents.assigned"))

    changed_at = utc_now_iso()

    with db:
        update = db.execute(
            """
            UPDATE incidents
            SET state = 'PENDIENTE_VALIDACION'
            WHERE id = ? AND state = 'EN_ATENCION' AND assigned_technician_id = ?
            """,
            (incident_id, g.user["id"]),
        )
        if update.rowcount != 1:
            raise RuntimeError("La incidencia cambió antes de registrar la solución.")

        db.execute(
            """
            INSERT INTO solutions (incident_id, technician_id, text, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (incident_id, g.user["id"], solution_text, changed_at),
        )

        db.execute(
            """
            INSERT INTO events
            (incident_id, actor_id, action, from_state, to_state, detail, created_at)
            VALUES (?, ?, 'SOLUCION_PROPUESTA', 'EN_ATENCION', 'PENDIENTE_VALIDACION', ?, ?)
            """,
            (incident_id, g.user["id"], solution_text, changed_at),
        )

    flash(f"Solución registrada para {incident['code']}.", "success")
    return redirect(url_for("incidents.assigned"))


@bp.post("/<int:incident_id>/confirm")
@role_required("SOLICITANTE")
def confirm_solution(incident_id):
    db = get_db()
    incident = get_owned_incident(incident_id)

    if incident["state"] != "PENDIENTE_VALIDACION":
        flash("La incidencia no está pendiente de validación.", "error")
        return redirect(url_for("incidents.index"))

    changed_at = utc_now_iso()

    with db:
        update = db.execute(
            """
            UPDATE incidents
            SET state = 'CERRADA', closed_at = ?
            WHERE id = ? AND state = 'PENDIENTE_VALIDACION' AND requester_id = ?
            """,
            (changed_at, incident_id, g.user["id"]),
        )
        if update.rowcount != 1:
            raise RuntimeError("La incidencia cambió antes de confirmar la solución.")

        db.execute(
            """
            INSERT INTO events
            (incident_id, actor_id, action, from_state, to_state, detail, created_at)
            VALUES (?, ?, 'CIERRE_CONFIRMADO', 'PENDIENTE_VALIDACION', 'CERRADA',
                    'Solución confirmada por el solicitante', ?)
            """,
            (incident_id, g.user["id"], changed_at),
        )

    flash(f"{incident['code']} cerrada por confirmación del solicitante.", "success")
    return redirect(url_for("incidents.index"))


@bp.post("/<int:incident_id>/reject")
@role_required("SOLICITANTE")
def reject_solution(incident_id):
    db = get_db()
    incident = get_owned_incident(incident_id)

    if incident["state"] != "PENDIENTE_VALIDACION":
        flash("La incidencia no está pendiente de validación.", "error")
        return redirect(url_for("incidents.index"))

    reason, error = validate_reason(request.form.get("reason", ""))
    if error:
        flash(error, "error")
        return redirect(url_for("incidents.index"))

    changed_at = utc_now_iso()

    with db:
        update = db.execute(
            """
            UPDATE incidents
            SET state = 'EN_ATENCION'
            WHERE id = ? AND state = 'PENDIENTE_VALIDACION' AND requester_id = ?
            """,
            (incident_id, g.user["id"]),
        )
        if update.rowcount != 1:
            raise RuntimeError("La incidencia cambió antes de rechazar la solución.")

        db.execute(
            """
            INSERT INTO events
            (incident_id, actor_id, action, from_state, to_state, detail, created_at)
            VALUES (?, ?, 'SOLUCION_RECHAZADA', 'PENDIENTE_VALIDACION', 'EN_ATENCION', ?, ?)
            """,
            (incident_id, g.user["id"], reason, changed_at),
        )

    flash(f"La solución de {incident['code']} fue rechazada.", "success")
    return redirect(url_for("incidents.index"))


@bp.post("/<int:incident_id>/reopen")
@role_required("SOLICITANTE")
def reopen_incident(incident_id):
    db = get_db()
    incident = get_owned_incident(incident_id)

    if incident["state"] != "CERRADA" or not incident["closed_at"]:
        flash("La incidencia no está cerrada.", "error")
        return redirect(url_for("incidents.index"))

    reason, error = validate_reason(request.form.get("reason", ""))
    if error:
        flash(error, "error")
        return redirect(url_for("incidents.index"))

    closed_at = datetime.fromisoformat(incident["closed_at"])
    if closed_at.tzinfo is None:
        closed_at = closed_at.replace(tzinfo=timezone.utc)

    elapsed = current_utc() - closed_at.astimezone(timezone.utc)
    if elapsed < timedelta(0) or elapsed > timedelta(hours=48):
        flash("La reapertura solo se permite hasta 48 horas después del último cierre.", "error")
        return redirect(url_for("incidents.index"))

    changed_at = utc_now_iso()

    with db:
        update = db.execute(
            """
            UPDATE incidents
            SET state = 'EN_ATENCION'
            WHERE id = ? AND state = 'CERRADA' AND requester_id = ?
            """,
            (incident_id, g.user["id"]),
        )
        if update.rowcount != 1:
            raise RuntimeError("La incidencia cambió antes de reabrirla.")

        db.execute(
            """
            INSERT INTO events
            (incident_id, actor_id, action, from_state, to_state, detail, created_at)
            VALUES (?, ?, 'REABIERTA', 'CERRADA', 'EN_ATENCION', ?, ?)
            """,
            (incident_id, g.user["id"], reason, changed_at),
        )

    flash(f"{incident['code']} reabierta y devuelta al mismo técnico.", "success")
    return redirect(url_for("incidents.index"))
