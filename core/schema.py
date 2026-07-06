SCHEMA_VERSION = 2
SCHEMA_SQL = r"""
CREATE TABLE IF NOT EXISTS schema_metadata (schema_version INTEGER NOT NULL, applied_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS event_identity (
 event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, request_id TEXT NOT NULL UNIQUE,
 occurred_at TEXT NOT NULL, committed_at TEXT NOT NULL, payload_json TEXT NOT NULL, payload_sha256 TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_history (
 audit_id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL, service_name TEXT NOT NULL,
 action_name TEXT NOT NULL, recorded_at TEXT NOT NULL, detail_json TEXT NOT NULL,
 FOREIGN KEY(event_id) REFERENCES event_identity(event_id)
);
CREATE TABLE IF NOT EXISTS assets (
 asset_id TEXT PRIMARY KEY, asset_name TEXT NOT NULL, asset_type TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('PLANNED','IN PROGRESS','COMPLETED','CANCELLED','REVIEW')),
 created_event_id TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL,
 FOREIGN KEY(created_event_id) REFERENCES event_identity(event_id)
);
CREATE TABLE IF NOT EXISTS inventory_authority (
 asset_id TEXT PRIMARY KEY, quantity INTEGER NOT NULL CHECK(quantity >= 0),
 total_cost_minor INTEGER NOT NULL CHECK(total_cost_minor >= 0),
 last_event_id TEXT NOT NULL UNIQUE, verified_at TEXT NOT NULL,
 FOREIGN KEY(asset_id) REFERENCES assets(asset_id), FOREIGN KEY(last_event_id) REFERENCES event_identity(event_id)
);
CREATE TABLE IF NOT EXISTS inventory_history (
 history_id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL UNIQUE, asset_id TEXT NOT NULL,
 quantity_delta INTEGER NOT NULL, cost_delta_minor INTEGER NOT NULL,
 resulting_quantity INTEGER NOT NULL CHECK(resulting_quantity >= 0),
 resulting_total_cost_minor INTEGER NOT NULL CHECK(resulting_total_cost_minor >= 0), recorded_at TEXT NOT NULL,
 FOREIGN KEY(event_id) REFERENCES event_identity(event_id), FOREIGN KEY(asset_id) REFERENCES assets(asset_id)
);
CREATE TRIGGER IF NOT EXISTS audit_history_no_update BEFORE UPDATE ON audit_history BEGIN SELECT RAISE(ABORT,'audit_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_history_no_delete BEFORE DELETE ON audit_history BEGIN SELECT RAISE(ABORT,'audit_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS event_identity_no_update BEFORE UPDATE ON event_identity BEGIN SELECT RAISE(ABORT,'event_identity is immutable'); END;
CREATE TRIGGER IF NOT EXISTS event_identity_no_delete BEFORE DELETE ON event_identity BEGIN SELECT RAISE(ABORT,'event_identity is immutable'); END;
CREATE TRIGGER IF NOT EXISTS inventory_history_no_update BEFORE UPDATE ON inventory_history BEGIN SELECT RAISE(ABORT,'inventory_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS inventory_history_no_delete BEFORE DELETE ON inventory_history BEGIN SELECT RAISE(ABORT,'inventory_history is append-only'); END;
"""
