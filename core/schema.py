SCHEMA_VERSION = 1
SCHEMA_SQL = r'''
CREATE TABLE IF NOT EXISTS schema_metadata (
    schema_version INTEGER NOT NULL,
    applied_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS event_identity (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    request_id TEXT NOT NULL UNIQUE,
    occurred_at TEXT NOT NULL,
    committed_at TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_history (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL,
    service_name TEXT NOT NULL,
    action_name TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    detail_json TEXT NOT NULL,
    FOREIGN KEY(event_id) REFERENCES event_identity(event_id)
);
CREATE TRIGGER IF NOT EXISTS audit_history_no_update
BEFORE UPDATE ON audit_history BEGIN SELECT RAISE(ABORT, 'audit_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_history_no_delete
BEFORE DELETE ON audit_history BEGIN SELECT RAISE(ABORT, 'audit_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS event_identity_no_update
BEFORE UPDATE ON event_identity BEGIN SELECT RAISE(ABORT, 'event_identity is immutable'); END;
CREATE TRIGGER IF NOT EXISTS event_identity_no_delete
BEFORE DELETE ON event_identity BEGIN SELECT RAISE(ABORT, 'event_identity is immutable'); END;
'''
