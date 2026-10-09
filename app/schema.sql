PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS solutions;
DROP TABLE IF EXISTS incidents;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('SOLICITANTE', 'COORDINADOR', 'TECNICO')),
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
);

CREATE TABLE incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    requester_id INTEGER NOT NULL,
    location TEXT NOT NULL CHECK (location IN ('LAB-01', 'AULA-201', 'BIB-01')),
    category TEXT NOT NULL CHECK (category IN ('ELECTRICIDAD', 'HIDRAULICA', 'MOBILIARIO', 'TIC')),
    description TEXT NOT NULL,
    impact TEXT NOT NULL CHECK (impact IN ('BAJO', 'ALTO')),
    risk_people INTEGER NOT NULL CHECK (risk_people IN (0, 1)),
    priority TEXT CHECK (priority IN ('NORMAL', 'ALTA', 'CRITICA') OR priority IS NULL),
    state TEXT NOT NULL DEFAULT 'REGISTRADA'
        CHECK (state IN ('REGISTRADA', 'ASIGNADA', 'EN_ATENCION', 'PENDIENTE_VALIDACION', 'CERRADA')),
    assigned_technician_id INTEGER,
    created_at TEXT NOT NULL,
    closed_at TEXT,
    FOREIGN KEY (requester_id) REFERENCES users(id),
    FOREIGN KEY (assigned_technician_id) REFERENCES users(id)
);

CREATE TABLE solutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    technician_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (incident_id) REFERENCES incidents(id),
    FOREIGN KEY (technician_id) REFERENCES users(id)
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    actor_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    from_state TEXT,
    to_state TEXT,
    detail TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (incident_id) REFERENCES incidents(id),
    FOREIGN KEY (actor_id) REFERENCES users(id)
);

CREATE INDEX idx_incidents_requester ON incidents(requester_id);
CREATE INDEX idx_incidents_state ON incidents(state);
CREATE INDEX idx_events_incident ON events(incident_id);
