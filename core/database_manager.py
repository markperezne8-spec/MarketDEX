from __future__ import annotations
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timezone
from .schema import SCHEMA_SQL, SCHEMA_VERSION
class DatabaseManager:
 def __init__(self,database_path:Path): self.database_path=Path(database_path); self.database_path.parent.mkdir(parents=True,exist_ok=True)
 def connect(self):
  c=sqlite3.connect(self.database_path); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); c.execute('PRAGMA journal_mode=WAL'); return c
 def initialize(self):
  with self.connect() as c:
   c.executescript(SCHEMA_SQL)
   row=c.execute('SELECT schema_version FROM schema_metadata ORDER BY rowid DESC LIMIT 1').fetchone()
   current=0 if row is None else int(row['schema_version'])
   if current > SCHEMA_VERSION: raise RuntimeError(f'Unsupported schema version: {current}')
   self._migrate_v3(c)
   self._repair_v5_renamed_foreign_keys(c)
   c.executescript(SCHEMA_SQL)
   if current < SCHEMA_VERSION: c.execute('INSERT INTO schema_metadata VALUES (?,?)',(SCHEMA_VERSION,datetime.now(timezone.utc).isoformat()))
 def _migrate_v3(self,c):
  # M23 requires one authoritative event to touch source and result rows.
  # Rebuild legacy M22 tables whose per-row event columns were incorrectly UNIQUE.
  asset_sql=(c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='assets'").fetchone() or {'sql':''})['sql'] or ''
  inv_sql=(c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='inventory_authority'").fetchone() or {'sql':''})['sql'] or ''
  if 'created_event_id TEXT NOT NULL UNIQUE' in asset_sql or 'last_event_id TEXT NOT NULL UNIQUE' in inv_sql:
   c.execute('PRAGMA foreign_keys=OFF')
   c.executescript("""
   DROP TRIGGER IF EXISTS inventory_history_no_update;
   DROP TRIGGER IF EXISTS inventory_history_no_delete;
   ALTER TABLE inventory_history RENAME TO inventory_history_v2;
   ALTER TABLE inventory_authority RENAME TO inventory_authority_v2;
   ALTER TABLE assets RENAME TO assets_v2;
   CREATE TABLE assets (asset_id TEXT PRIMARY KEY, asset_name TEXT NOT NULL, asset_type TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN ('PLANNED','IN PROGRESS','COMPLETED','CANCELLED','REVIEW')), created_event_id TEXT NOT NULL, created_at TEXT NOT NULL, FOREIGN KEY(created_event_id) REFERENCES event_identity(event_id));
   CREATE TABLE inventory_authority (asset_id TEXT PRIMARY KEY, quantity INTEGER NOT NULL CHECK(quantity >= 0), total_cost_minor INTEGER NOT NULL CHECK(total_cost_minor >= 0), last_event_id TEXT NOT NULL, verified_at TEXT NOT NULL, FOREIGN KEY(asset_id) REFERENCES assets(asset_id), FOREIGN KEY(last_event_id) REFERENCES event_identity(event_id));
   CREATE TABLE inventory_history (history_id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL, asset_id TEXT NOT NULL, quantity_delta INTEGER NOT NULL, cost_delta_minor INTEGER NOT NULL, resulting_quantity INTEGER NOT NULL CHECK(resulting_quantity >= 0), resulting_total_cost_minor INTEGER NOT NULL CHECK(resulting_total_cost_minor >= 0), recorded_at TEXT NOT NULL, UNIQUE(event_id,asset_id), FOREIGN KEY(event_id) REFERENCES event_identity(event_id), FOREIGN KEY(asset_id) REFERENCES assets(asset_id));
   INSERT INTO assets SELECT * FROM assets_v2;
   INSERT INTO inventory_authority SELECT * FROM inventory_authority_v2;
   INSERT INTO inventory_history SELECT * FROM inventory_history_v2;
   DROP TABLE inventory_history_v2;
   DROP TABLE inventory_authority_v2;
   DROP TABLE assets_v2;
   CREATE TRIGGER inventory_history_no_update BEFORE UPDATE ON inventory_history BEGIN SELECT RAISE(ABORT,'inventory_history is append-only'); END;
   CREATE TRIGGER inventory_history_no_delete BEFORE DELETE ON inventory_history BEGIN SELECT RAISE(ABORT,'inventory_history is append-only'); END;
   """)
   c.execute('PRAGMA foreign_keys=ON')
 def _repair_v5_renamed_foreign_keys(self,c):
  # SQLite may rewrite dependent FK targets during legacy table renames.
  # Repair any M23 database whose transformation tables still point at *_v2.
  trow=c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='transformations'").fetchone()
  lrow=c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='transformation_lineage'").fetchone()
  tsql='' if trow is None else (trow['sql'] or '')
  lsql='' if lrow is None else (lrow['sql'] or '')
  if '_v2' not in tsql and '_v2' not in lsql:
   return
  c.execute('PRAGMA foreign_keys=OFF')
  c.executescript("""
  CREATE TABLE transformations_repair (
   transformation_id TEXT PRIMARY KEY,
   source_asset_id TEXT NOT NULL,
   source_quantity INTEGER NOT NULL CHECK(source_quantity > 0),
   source_cost_minor INTEGER NOT NULL CHECK(source_cost_minor >= 0),
   state TEXT NOT NULL CHECK(state IN ('PLANNED','IN PROGRESS','COMPLETED','CANCELLED','REVIEW')),
   created_event_id TEXT NOT NULL UNIQUE,
   completed_event_id TEXT UNIQUE,
   created_at TEXT NOT NULL,
   completed_at TEXT,
   FOREIGN KEY(source_asset_id) REFERENCES assets(asset_id)
  );
  INSERT INTO transformations_repair SELECT * FROM transformations;
  CREATE TABLE transformation_lineage_repair (
   lineage_id INTEGER PRIMARY KEY AUTOINCREMENT,
   transformation_id TEXT NOT NULL,
   source_asset_id TEXT NOT NULL,
   result_asset_id TEXT NOT NULL,
   allocated_cost_minor INTEGER NOT NULL CHECK(allocated_cost_minor >= 0),
   result_quantity INTEGER NOT NULL CHECK(result_quantity > 0),
   event_id TEXT NOT NULL,
   recorded_at TEXT NOT NULL,
   UNIQUE(transformation_id,result_asset_id),
   FOREIGN KEY(transformation_id) REFERENCES transformations_repair(transformation_id),
   FOREIGN KEY(source_asset_id) REFERENCES assets(asset_id),
   FOREIGN KEY(result_asset_id) REFERENCES assets(asset_id)
  );
  INSERT INTO transformation_lineage_repair SELECT * FROM transformation_lineage;
  DROP TRIGGER IF EXISTS transformation_lineage_no_update;
  DROP TRIGGER IF EXISTS transformation_lineage_no_delete;
  DROP TABLE transformation_lineage;
  DROP TABLE transformations;
  ALTER TABLE transformations_repair RENAME TO transformations;
  ALTER TABLE transformation_lineage_repair RENAME TO transformation_lineage;
  CREATE TRIGGER transformation_lineage_no_update BEFORE UPDATE ON transformation_lineage BEGIN SELECT RAISE(ABORT,'transformation_lineage is append-only'); END;
  CREATE TRIGGER transformation_lineage_no_delete BEFORE DELETE ON transformation_lineage BEGIN SELECT RAISE(ABORT,'transformation_lineage is append-only'); END;
  """)
  c.execute('PRAGMA foreign_keys=ON')

 @contextmanager
 def transaction(self):
  c=self.connect()
  try: c.execute('BEGIN IMMEDIATE'); yield c; c.commit()
  except Exception: c.rollback(); raise
  finally: c.close()
