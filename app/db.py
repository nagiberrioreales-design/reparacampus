import sqlite3
from pathlib import Path

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash


TEST_PASSWORD = "Campus2026!"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def seed_users(db):
    users = [
        ("solicitante1", "Solicitante Uno", "SOLICITANTE", 1),
        ("solicitante2", "Solicitante Dos", "SOLICITANTE", 1),
        ("coordinador", "Coordinador Campus", "COORDINADOR", 1),
        ("tecnico1", "Técnico Uno", "TECNICO", 1),
        ("tecnico2", "Técnico Dos", "TECNICO", 1),
    ]
    for username, display_name, role, active in users:
        db.execute(
            """
            INSERT INTO users (username, display_name, password_hash, role, active)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, display_name, generate_password_hash(TEST_PASSWORD), role, active),
        )


def init_db():
    db = get_db()
    schema_path = Path(__file__).with_name("schema.sql")
    db.executescript(schema_path.read_text(encoding="utf-8"))
    seed_users(db)
    db.commit()


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Base de datos inicializada con cuentas ficticias.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
