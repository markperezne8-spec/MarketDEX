SCHEMA_VERSION = 6
SCHEMA_SQL = r"""
CREATE TABLE IF NOT EXISTS schema_metadata (schema_version INTEGER NOT NULL, applied_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS event_identity (event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, request_id TEXT NOT NULL UNIQUE, occurred_at TEXT NOT NULL, committed_at TEXT NOT NULL, payload_json TEXT NOT NULL, payload_sha256 TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit_history (audit_id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL, service_name TEXT NOT NULL, action_name TEXT NOT NULL, recorded_at TEXT NOT NULL, detail_json TEXT NOT NULL, FOREIGN KEY(event_id) REFERENCES event_identity(event_id));
CREATE TABLE IF NOT EXISTS assets (asset_id TEXT PRIMARY KEY, asset_name TEXT NOT NULL, asset_type TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN ('PLANNED','IN PROGRESS','COMPLETED','CANCELLED','REVIEW')), created_event_id TEXT NOT NULL, created_at TEXT NOT NULL, FOREIGN KEY(created_event_id) REFERENCES event_identity(event_id));
CREATE TABLE IF NOT EXISTS inventory_authority (asset_id TEXT PRIMARY KEY, quantity INTEGER NOT NULL CHECK(quantity >= 0), total_cost_minor INTEGER NOT NULL CHECK(total_cost_minor >= 0), last_event_id TEXT NOT NULL, verified_at TEXT NOT NULL, FOREIGN KEY(asset_id) REFERENCES assets(asset_id), FOREIGN KEY(last_event_id) REFERENCES event_identity(event_id));
CREATE TABLE IF NOT EXISTS inventory_history (history_id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL, asset_id TEXT NOT NULL, quantity_delta INTEGER NOT NULL, cost_delta_minor INTEGER NOT NULL, resulting_quantity INTEGER NOT NULL CHECK(resulting_quantity >= 0), resulting_total_cost_minor INTEGER NOT NULL CHECK(resulting_total_cost_minor >= 0), recorded_at TEXT NOT NULL, UNIQUE(event_id,asset_id), FOREIGN KEY(event_id) REFERENCES event_identity(event_id), FOREIGN KEY(asset_id) REFERENCES assets(asset_id));
CREATE TABLE IF NOT EXISTS sales (
 sale_id TEXT PRIMARY KEY,
 asset_id TEXT NOT NULL,
 quantity INTEGER NOT NULL CHECK(quantity > 0),
 revenue_minor INTEGER NOT NULL CHECK(revenue_minor >= 0),
 marketplace_fees_minor INTEGER NOT NULL CHECK(marketplace_fees_minor >= 0),
 shipping_minor INTEGER NOT NULL CHECK(shipping_minor >= 0),
 packaging_minor INTEGER NOT NULL CHECK(packaging_minor >= 0),
 cogs_minor INTEGER NOT NULL CHECK(cogs_minor >= 0),
 profit_minor INTEGER NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('COMPLETED','REVIEW')),
 created_event_id TEXT NOT NULL UNIQUE,
 created_at TEXT NOT NULL,
 FOREIGN KEY(asset_id) REFERENCES assets(asset_id),
 FOREIGN KEY(created_event_id) REFERENCES event_identity(event_id)
);
CREATE TABLE IF NOT EXISTS sales_financial_history (
 financial_history_id INTEGER PRIMARY KEY AUTOINCREMENT,
 event_id TEXT NOT NULL UNIQUE,
 sale_id TEXT NOT NULL,
 revenue_minor INTEGER NOT NULL,
 marketplace_fees_minor INTEGER NOT NULL,
 shipping_minor INTEGER NOT NULL,
 packaging_minor INTEGER NOT NULL,
 cogs_minor INTEGER NOT NULL,
 profit_minor INTEGER NOT NULL,
 recorded_at TEXT NOT NULL,
 FOREIGN KEY(event_id) REFERENCES event_identity(event_id),
 FOREIGN KEY(sale_id) REFERENCES sales(sale_id)
);
CREATE TABLE IF NOT EXISTS transformations (transformation_id TEXT PRIMARY KEY, source_asset_id TEXT NOT NULL, source_quantity INTEGER NOT NULL CHECK(source_quantity > 0), source_cost_minor INTEGER NOT NULL CHECK(source_cost_minor >= 0), state TEXT NOT NULL CHECK(state IN ('PLANNED','IN PROGRESS','COMPLETED','CANCELLED','REVIEW')), created_event_id TEXT NOT NULL, completed_event_id TEXT UNIQUE, created_at TEXT NOT NULL, completed_at TEXT, FOREIGN KEY(source_asset_id) REFERENCES assets(asset_id));
CREATE TABLE IF NOT EXISTS transformation_lineage (lineage_id INTEGER PRIMARY KEY AUTOINCREMENT, transformation_id TEXT NOT NULL, source_asset_id TEXT NOT NULL, result_asset_id TEXT NOT NULL, allocated_cost_minor INTEGER NOT NULL CHECK(allocated_cost_minor >= 0), result_quantity INTEGER NOT NULL CHECK(result_quantity > 0), event_id TEXT NOT NULL, recorded_at TEXT NOT NULL, UNIQUE(transformation_id,result_asset_id), FOREIGN KEY(transformation_id) REFERENCES transformations(transformation_id), FOREIGN KEY(source_asset_id) REFERENCES assets(asset_id), FOREIGN KEY(result_asset_id) REFERENCES assets(asset_id));
CREATE TRIGGER IF NOT EXISTS audit_history_no_update BEFORE UPDATE ON audit_history BEGIN SELECT RAISE(ABORT,'audit_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_history_no_delete BEFORE DELETE ON audit_history BEGIN SELECT RAISE(ABORT,'audit_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS event_identity_no_update BEFORE UPDATE ON event_identity BEGIN SELECT RAISE(ABORT,'event_identity is immutable'); END;
CREATE TRIGGER IF NOT EXISTS event_identity_no_delete BEFORE DELETE ON event_identity BEGIN SELECT RAISE(ABORT,'event_identity is immutable'); END;
CREATE TRIGGER IF NOT EXISTS inventory_history_no_update BEFORE UPDATE ON inventory_history BEGIN SELECT RAISE(ABORT,'inventory_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS inventory_history_no_delete BEFORE DELETE ON inventory_history BEGIN SELECT RAISE(ABORT,'inventory_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS sales_financial_history_no_update BEFORE UPDATE ON sales_financial_history BEGIN SELECT RAISE(ABORT,'sales_financial_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS sales_financial_history_no_delete BEFORE DELETE ON sales_financial_history BEGIN SELECT RAISE(ABORT,'sales_financial_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS transformation_lineage_no_update BEFORE UPDATE ON transformation_lineage BEGIN SELECT RAISE(ABORT,'transformation_lineage is append-only'); END;
CREATE TRIGGER IF NOT EXISTS transformation_lineage_no_delete BEFORE DELETE ON transformation_lineage BEGIN SELECT RAISE(ABORT,'transformation_lineage is append-only'); END;
"""
