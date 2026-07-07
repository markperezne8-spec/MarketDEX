SCHEMA_VERSION = 10
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

CREATE TABLE IF NOT EXISTS returns (
 return_id TEXT PRIMARY KEY, sale_id TEXT NOT NULL, asset_id TEXT NOT NULL,
 quantity INTEGER NOT NULL CHECK(quantity > 0), condition_evidence TEXT NOT NULL,
 restock_authorized INTEGER NOT NULL CHECK(restock_authorized IN (0,1)),
 refund_minor INTEGER NOT NULL CHECK(refund_minor >= 0),
 restored_cost_minor INTEGER NOT NULL CHECK(restored_cost_minor >= 0),
 profit_restatement_minor INTEGER NOT NULL, event_id TEXT NOT NULL UNIQUE,
 created_at TEXT NOT NULL, FOREIGN KEY(sale_id) REFERENCES sales(sale_id),
 FOREIGN KEY(asset_id) REFERENCES assets(asset_id), FOREIGN KEY(event_id) REFERENCES event_identity(event_id)
);
CREATE TABLE IF NOT EXISTS return_events (
 return_event_id INTEGER PRIMARY KEY AUTOINCREMENT, return_id TEXT NOT NULL,
 original_event_id TEXT NOT NULL, event_id TEXT NOT NULL UNIQUE, recorded_at TEXT NOT NULL,
 FOREIGN KEY(return_id) REFERENCES returns(return_id), FOREIGN KEY(original_event_id) REFERENCES event_identity(event_id),
 FOREIGN KEY(event_id) REFERENCES event_identity(event_id)
);
CREATE TABLE IF NOT EXISTS correction_events (
 correction_event_id TEXT PRIMARY KEY, original_event_id TEXT NOT NULL, corrective_evidence TEXT NOT NULL,
 inventory_quantity_delta INTEGER NOT NULL, inventory_cost_delta_minor INTEGER NOT NULL,
 financial_delta_minor INTEGER NOT NULL, event_id TEXT NOT NULL UNIQUE, recorded_at TEXT NOT NULL,
 FOREIGN KEY(original_event_id) REFERENCES event_identity(event_id), FOREIGN KEY(event_id) REFERENCES event_identity(event_id)
);
CREATE TABLE IF NOT EXISTS reversal_events (
 reversal_event_id TEXT PRIMARY KEY, original_event_id TEXT NOT NULL,
 inventory_quantity_delta INTEGER NOT NULL, inventory_cost_delta_minor INTEGER NOT NULL,
 financial_delta_minor INTEGER NOT NULL, event_id TEXT NOT NULL UNIQUE, recorded_at TEXT NOT NULL,
 FOREIGN KEY(original_event_id) REFERENCES event_identity(event_id), FOREIGN KEY(event_id) REFERENCES event_identity(event_id)
);
CREATE TABLE IF NOT EXISTS inventory_movements (
 movement_id TEXT PRIMARY KEY, asset_id TEXT NOT NULL, event_id TEXT NOT NULL,
 quantity_delta INTEGER NOT NULL, cost_delta_minor INTEGER NOT NULL, movement_type TEXT NOT NULL,
 recorded_at TEXT NOT NULL, UNIQUE(event_id,asset_id,movement_type),
 FOREIGN KEY(asset_id) REFERENCES assets(asset_id), FOREIGN KEY(event_id) REFERENCES event_identity(event_id)
);
CREATE TABLE IF NOT EXISTS financial_events (
 financial_event_id TEXT PRIMARY KEY, event_id TEXT NOT NULL UNIQUE, original_event_id TEXT,
 sale_id TEXT, event_type TEXT NOT NULL, amount_minor INTEGER NOT NULL, profit_effect_minor INTEGER NOT NULL,
 recorded_at TEXT NOT NULL, FOREIGN KEY(event_id) REFERENCES event_identity(event_id),
 FOREIGN KEY(original_event_id) REFERENCES event_identity(event_id), FOREIGN KEY(sale_id) REFERENCES sales(sale_id)
);
CREATE TABLE IF NOT EXISTS event_history (
 history_id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL UNIQUE, original_event_id TEXT,
 authority_type TEXT NOT NULL, authority_id TEXT NOT NULL, recorded_at TEXT NOT NULL,
 FOREIGN KEY(event_id) REFERENCES event_identity(event_id), FOREIGN KEY(original_event_id) REFERENCES event_identity(event_id)
);
CREATE TABLE IF NOT EXISTS audit_events (
 audit_event_id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL, authority_type TEXT NOT NULL,
 authority_id TEXT NOT NULL, verification_result TEXT NOT NULL, recorded_at TEXT NOT NULL,
 UNIQUE(event_id,authority_type,authority_id), FOREIGN KEY(event_id) REFERENCES event_identity(event_id)
);

CREATE TABLE IF NOT EXISTS exception_authority (
 exception_id TEXT PRIMARY KEY,
 source_event_id TEXT,
 exception_type TEXT NOT NULL,
 evidence TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('REVIEW','COMPLETED')),
 event_id TEXT NOT NULL UNIQUE,
 created_at TEXT NOT NULL,
 FOREIGN KEY(source_event_id) REFERENCES event_identity(event_id),
 FOREIGN KEY(event_id) REFERENCES event_identity(event_id)
);
CREATE TABLE IF NOT EXISTS exception_history (
 exception_history_id INTEGER PRIMARY KEY AUTOINCREMENT,
 exception_id TEXT NOT NULL,
 event_id TEXT NOT NULL UNIQUE,
 source_event_id TEXT,
 exception_type TEXT NOT NULL,
 evidence TEXT NOT NULL,
 state TEXT NOT NULL,
 recorded_at TEXT NOT NULL,
 FOREIGN KEY(exception_id) REFERENCES exception_authority(exception_id),
 FOREIGN KEY(event_id) REFERENCES event_identity(event_id),
 FOREIGN KEY(source_event_id) REFERENCES event_identity(event_id)
);
CREATE TABLE IF NOT EXISTS audit_verifications (
 audit_verification_id TEXT PRIMARY KEY,
 target_event_id TEXT NOT NULL,
 target_payload_sha256 TEXT NOT NULL,
 verification_result TEXT NOT NULL CHECK(verification_result IN ('VERIFIED','FAILED')),
 event_id TEXT NOT NULL UNIQUE,
 verified_at TEXT NOT NULL,
 FOREIGN KEY(target_event_id) REFERENCES event_identity(event_id),
 FOREIGN KEY(event_id) REFERENCES event_identity(event_id)
);
CREATE TABLE IF NOT EXISTS replay_defense_history (
 replay_history_id INTEGER PRIMARY KEY AUTOINCREMENT,
 request_id TEXT NOT NULL,
 original_event_id TEXT NOT NULL,
 attempted_event_type TEXT NOT NULL,
 payload_sha256 TEXT NOT NULL,
 defense_result TEXT NOT NULL CHECK(defense_result='BLOCKED'),
 recorded_at TEXT NOT NULL,
 UNIQUE(request_id,attempted_event_type,payload_sha256),
 FOREIGN KEY(original_event_id) REFERENCES event_identity(event_id)
);

CREATE TABLE IF NOT EXISTS marketplace_allocations (
 allocation_id TEXT PRIMARY KEY,
 asset_id TEXT NOT NULL,
 marketplace TEXT NOT NULL,
 allocated_quantity INTEGER NOT NULL CHECK(allocated_quantity > 0),
 state TEXT NOT NULL CHECK(state IN ('ACTIVE','RELEASED')),
 publication_reference TEXT,
 event_id TEXT NOT NULL UNIQUE,
 created_at TEXT NOT NULL,
 FOREIGN KEY(asset_id) REFERENCES assets(asset_id),
 FOREIGN KEY(event_id) REFERENCES event_identity(event_id)
);
CREATE TABLE IF NOT EXISTS settlements (
 settlement_reference TEXT PRIMARY KEY,
 sale_id TEXT NOT NULL UNIQUE,
 settled_minor INTEGER NOT NULL CHECK(settled_minor >= 0),
 event_id TEXT NOT NULL UNIQUE,
 created_at TEXT NOT NULL,
 FOREIGN KEY(sale_id) REFERENCES sales(sale_id),
 FOREIGN KEY(event_id) REFERENCES event_identity(event_id)
);
CREATE TABLE IF NOT EXISTS order_closures (
 sale_id TEXT PRIMARY KEY,
 settlement_reference TEXT NOT NULL,
 event_id TEXT NOT NULL UNIQUE,
 closed_at TEXT NOT NULL,
 FOREIGN KEY(sale_id) REFERENCES sales(sale_id),
 FOREIGN KEY(settlement_reference) REFERENCES settlements(settlement_reference),
 FOREIGN KEY(event_id) REFERENCES event_identity(event_id)
);
CREATE TABLE IF NOT EXISTS exception_resolutions (
 resolution_event_id TEXT PRIMARY KEY,
 exception_id TEXT NOT NULL UNIQUE,
 explicit_request_id TEXT NOT NULL UNIQUE,
 evidence TEXT NOT NULL,
 event_id TEXT NOT NULL UNIQUE,
 resolved_at TEXT NOT NULL,
 FOREIGN KEY(exception_id) REFERENCES exception_authority(exception_id),
 FOREIGN KEY(event_id) REFERENCES event_identity(event_id)
);

CREATE TABLE IF NOT EXISTS inventory_adjustments (
 adjustment_id TEXT PRIMARY KEY,
 asset_id TEXT NOT NULL,
 adjustment_type TEXT NOT NULL CHECK(adjustment_type IN ('DAMAGE','LOSS')),
 adjustment_quantity INTEGER NOT NULL CHECK(adjustment_quantity > 0),
 evidence_type TEXT NOT NULL,
 evidence_reference TEXT NOT NULL,
 evidence_complete INTEGER NOT NULL CHECK(evidence_complete=1),
 request_id TEXT NOT NULL UNIQUE,
 replay_key TEXT NOT NULL UNIQUE,
 movement_id TEXT NOT NULL UNIQUE,
 event_id TEXT NOT NULL UNIQUE,
 control_result TEXT NOT NULL CHECK(control_result='CONTROLLED'),
 committed_at TEXT NOT NULL,
 verified_at TEXT NOT NULL,
 FOREIGN KEY(asset_id) REFERENCES assets(asset_id),
 FOREIGN KEY(event_id) REFERENCES event_identity(event_id),
 FOREIGN KEY(movement_id) REFERENCES inventory_movements(movement_id)
);
CREATE TABLE IF NOT EXISTS transformations (transformation_id TEXT PRIMARY KEY, source_asset_id TEXT NOT NULL, source_quantity INTEGER NOT NULL CHECK(source_quantity > 0), source_cost_minor INTEGER NOT NULL CHECK(source_cost_minor >= 0), state TEXT NOT NULL CHECK(state IN ('PLANNED','IN PROGRESS','COMPLETED','CANCELLED','REVIEW')), created_event_id TEXT NOT NULL, completed_event_id TEXT UNIQUE, created_at TEXT NOT NULL, completed_at TEXT, FOREIGN KEY(source_asset_id) REFERENCES assets(asset_id));
CREATE TABLE IF NOT EXISTS transformation_lineage (lineage_id INTEGER PRIMARY KEY AUTOINCREMENT, transformation_id TEXT NOT NULL, source_asset_id TEXT NOT NULL, result_asset_id TEXT NOT NULL, allocated_cost_minor INTEGER NOT NULL CHECK(allocated_cost_minor >= 0), result_quantity INTEGER NOT NULL CHECK(result_quantity > 0), event_id TEXT NOT NULL, recorded_at TEXT NOT NULL, UNIQUE(transformation_id,result_asset_id), FOREIGN KEY(transformation_id) REFERENCES transformations(transformation_id), FOREIGN KEY(source_asset_id) REFERENCES assets(asset_id), FOREIGN KEY(result_asset_id) REFERENCES assets(asset_id));
CREATE TRIGGER IF NOT EXISTS audit_history_no_update BEFORE UPDATE ON audit_history BEGIN SELECT RAISE(ABORT,'audit_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_history_no_delete BEFORE DELETE ON audit_history BEGIN SELECT RAISE(ABORT,'audit_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS event_identity_no_update BEFORE UPDATE ON event_identity BEGIN SELECT RAISE(ABORT,'event_identity is immutable'); END;
CREATE TRIGGER IF NOT EXISTS event_identity_no_delete BEFORE DELETE ON event_identity BEGIN SELECT RAISE(ABORT,'event_identity is immutable'); END;
CREATE TRIGGER IF NOT EXISTS inventory_history_no_update BEFORE UPDATE ON inventory_history BEGIN SELECT RAISE(ABORT,'inventory_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS inventory_history_no_delete BEFORE DELETE ON inventory_history BEGIN SELECT RAISE(ABORT,'inventory_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS return_events_no_update BEFORE UPDATE ON return_events BEGIN SELECT RAISE(ABORT,'return_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS return_events_no_delete BEFORE DELETE ON return_events BEGIN SELECT RAISE(ABORT,'return_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS correction_events_no_update BEFORE UPDATE ON correction_events BEGIN SELECT RAISE(ABORT,'correction_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS correction_events_no_delete BEFORE DELETE ON correction_events BEGIN SELECT RAISE(ABORT,'correction_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS reversal_events_no_update BEFORE UPDATE ON reversal_events BEGIN SELECT RAISE(ABORT,'reversal_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS reversal_events_no_delete BEFORE DELETE ON reversal_events BEGIN SELECT RAISE(ABORT,'reversal_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS inventory_movements_no_update BEFORE UPDATE ON inventory_movements BEGIN SELECT RAISE(ABORT,'inventory_movements is append-only'); END;
CREATE TRIGGER IF NOT EXISTS inventory_movements_no_delete BEFORE DELETE ON inventory_movements BEGIN SELECT RAISE(ABORT,'inventory_movements is append-only'); END;
CREATE TRIGGER IF NOT EXISTS financial_events_no_update BEFORE UPDATE ON financial_events BEGIN SELECT RAISE(ABORT,'financial_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS financial_events_no_delete BEFORE DELETE ON financial_events BEGIN SELECT RAISE(ABORT,'financial_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS event_history_no_update BEFORE UPDATE ON event_history BEGIN SELECT RAISE(ABORT,'event_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS event_history_no_delete BEFORE DELETE ON event_history BEGIN SELECT RAISE(ABORT,'event_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_events_no_update BEFORE UPDATE ON audit_events BEGIN SELECT RAISE(ABORT,'audit_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_events_no_delete BEFORE DELETE ON audit_events BEGIN SELECT RAISE(ABORT,'audit_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS exception_history_no_update BEFORE UPDATE ON exception_history BEGIN SELECT RAISE(ABORT,'exception_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS exception_history_no_delete BEFORE DELETE ON exception_history BEGIN SELECT RAISE(ABORT,'exception_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_verifications_no_update BEFORE UPDATE ON audit_verifications BEGIN SELECT RAISE(ABORT,'audit_verifications is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_verifications_no_delete BEFORE DELETE ON audit_verifications BEGIN SELECT RAISE(ABORT,'audit_verifications is append-only'); END;
CREATE TRIGGER IF NOT EXISTS replay_defense_history_no_update BEFORE UPDATE ON replay_defense_history BEGIN SELECT RAISE(ABORT,'replay_defense_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS replay_defense_history_no_delete BEFORE DELETE ON replay_defense_history BEGIN SELECT RAISE(ABORT,'replay_defense_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS marketplace_allocations_no_update BEFORE UPDATE ON marketplace_allocations BEGIN SELECT RAISE(ABORT,'marketplace_allocations is append-only'); END;
CREATE TRIGGER IF NOT EXISTS marketplace_allocations_no_delete BEFORE DELETE ON marketplace_allocations BEGIN SELECT RAISE(ABORT,'marketplace_allocations is append-only'); END;
CREATE TRIGGER IF NOT EXISTS settlements_no_update BEFORE UPDATE ON settlements BEGIN SELECT RAISE(ABORT,'settlements is append-only'); END;
CREATE TRIGGER IF NOT EXISTS settlements_no_delete BEFORE DELETE ON settlements BEGIN SELECT RAISE(ABORT,'settlements is append-only'); END;
CREATE TRIGGER IF NOT EXISTS order_closures_no_update BEFORE UPDATE ON order_closures BEGIN SELECT RAISE(ABORT,'order_closures is append-only'); END;
CREATE TRIGGER IF NOT EXISTS order_closures_no_delete BEFORE DELETE ON order_closures BEGIN SELECT RAISE(ABORT,'order_closures is append-only'); END;
CREATE TRIGGER IF NOT EXISTS exception_resolutions_no_update BEFORE UPDATE ON exception_resolutions BEGIN SELECT RAISE(ABORT,'exception_resolutions is append-only'); END;
CREATE TRIGGER IF NOT EXISTS exception_resolutions_no_delete BEFORE DELETE ON exception_resolutions BEGIN SELECT RAISE(ABORT,'exception_resolutions is append-only'); END;
CREATE TRIGGER IF NOT EXISTS inventory_adjustments_no_update BEFORE UPDATE ON inventory_adjustments BEGIN SELECT RAISE(ABORT,'inventory_adjustments is append-only'); END;
CREATE TRIGGER IF NOT EXISTS inventory_adjustments_no_delete BEFORE DELETE ON inventory_adjustments BEGIN SELECT RAISE(ABORT,'inventory_adjustments is append-only'); END;
CREATE TRIGGER IF NOT EXISTS sales_financial_history_no_update BEFORE UPDATE ON sales_financial_history BEGIN SELECT RAISE(ABORT,'sales_financial_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS sales_financial_history_no_delete BEFORE DELETE ON sales_financial_history BEGIN SELECT RAISE(ABORT,'sales_financial_history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS transformation_lineage_no_update BEFORE UPDATE ON transformation_lineage BEGIN SELECT RAISE(ABORT,'transformation_lineage is append-only'); END;
CREATE TRIGGER IF NOT EXISTS transformation_lineage_no_delete BEFORE DELETE ON transformation_lineage BEGIN SELECT RAISE(ABORT,'transformation_lineage is append-only'); END;
"""
