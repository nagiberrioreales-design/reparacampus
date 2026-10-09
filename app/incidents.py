from datetime import datetime, timezone
from uuid import uuid4

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from .auth import role_required
from .db import get_db
from .domain import validate_new_incident


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
