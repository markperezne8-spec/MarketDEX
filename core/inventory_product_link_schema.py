SCHEMA_VERSION = 25

SCHEMA_SQL = r'''
CREATE TABLE IF NOT EXISTS inventory_product_links (
    inventory_product_link_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL UNIQUE,
    product_id TEXT NOT NULL,
    state TEXT NOT NULL CHECK(state='LINKED'),
    created_event_id TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    FOREIGN KEY(asset_id) REFERENCES assets(asset_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);
CREATE TABLE IF NOT EXISTS inventory_product_link_history (
    linkage_history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_product_link_id TEXT NOT NULL,
    asset_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    linkage_request_id TEXT NOT NULL,
    event_id TEXT NOT NULL,
    resulting_state TEXT NOT NULL,
    recorded_at TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS inventory_product_link_history_no_update
BEFORE UPDATE ON inventory_product_link_history
BEGIN SELECT RAISE(ABORT,'inventory product link history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS inventory_product_link_history_no_delete
BEFORE DELETE ON inventory_product_link_history
BEGIN SELECT RAISE(ABORT,'inventory product link history is append-only'); END;
'''