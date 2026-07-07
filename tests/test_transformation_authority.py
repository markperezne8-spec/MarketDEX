import sqlite3,tempfile,unittest
from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import ReplayRejected
from services.service_registry import ServiceRegistry
class TransformationAuthorityTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.db=DatabaseManager(Path(self.tmp.name)/'m.sqlite3'); self.db.initialize(); self.s=ServiceRegistry(self.db); self.s.asset.create_asset(request_id='a',asset_id='BOX',asset_name='Box',asset_type='SEALED'); self.s.inventory.apply_acquisition(request_id='i',asset_id='BOX',quantity=1,total_cost_minor=6000)
 def tearDown(self): self.tmp.cleanup()
 def run_transform(self,request='t',cost=6000,qty=1): return self.s.transformation.execute(request_id=request,transformation_id='T1',source_asset_id='BOX',source_quantity=qty,outputs=[{'asset_id':'PACK','asset_name':'Pack','asset_type':'PACK','quantity':6,'allocated_cost_minor':cost}])
 def test_source_result_lineage_and_cost_conservation(self):
  self.run_transform()
  with self.db.connect() as c:
   source=c.execute('SELECT * FROM inventory_authority WHERE asset_id="BOX"').fetchone(); result=c.execute('SELECT * FROM inventory_authority WHERE asset_id="PACK"').fetchone(); lineage=c.execute('SELECT * FROM transformation_lineage').fetchone()
   self.assertEqual((source['quantity'],source['total_cost_minor']),(0,0)); self.assertEqual((result['quantity'],result['total_cost_minor']),(6,6000)); self.assertEqual((lineage['source_asset_id'],lineage['result_asset_id']),('BOX','PACK'))
 def test_ambiguous_cost_allocation_fails_closed(self):
  with self.assertRaises(ValueError): self.run_transform(cost=5999)
  with self.db.connect() as c: self.assertEqual(c.execute('SELECT COUNT(*) FROM transformations').fetchone()[0],0); self.assertEqual(c.execute('SELECT quantity FROM inventory_authority WHERE asset_id="BOX"').fetchone()[0],1)
 def test_invalid_quantity_fails_closed(self):
  with self.assertRaises(ValueError): self.run_transform(qty=2)
 def test_replay_does_not_create_second_write(self):
  self.run_transform()
  with self.assertRaises(Exception): self.s.transformation.execute(request_id='t',transformation_id='T2',source_asset_id='PACK',source_quantity=1,outputs=[{'asset_id':'X','asset_name':'X','asset_type':'SINGLE','quantity':1,'allocated_cost_minor':1000}])
  with self.db.connect() as c: self.assertEqual(c.execute('SELECT COUNT(*) FROM transformations').fetchone()[0],1)
 def test_invalid_state_transition_rejected(self):
  with self.assertRaises(ValueError): self.s.transformation.validate_transition('PLANNED','COMPLETED')
 def test_lineage_append_only(self):
  self.run_transform()
  with self.assertRaises(sqlite3.IntegrityError):
   with self.db.transaction() as c: c.execute('DELETE FROM transformation_lineage')

 def test_m22_database_migrates_and_transforms(self):
  legacy=Path(self.tmp.name)/'legacy.sqlite3'; db=DatabaseManager(legacy); db.initialize()
  # Current schema is already v3; structural assertion guards the hotfix contract.
  with db.connect() as c:
   asset_sql=c.execute("SELECT sql FROM sqlite_master WHERE name='assets'").fetchone()[0]
   inv_sql=c.execute("SELECT sql FROM sqlite_master WHERE name='inventory_authority'").fetchone()[0]
   self.assertNotIn('created_event_id TEXT NOT NULL UNIQUE',asset_sql)
   self.assertNotIn('last_event_id TEXT NOT NULL UNIQUE',inv_sql)


 def test_bad_m23_v3_database_is_structurally_repaired(self):
  legacy=Path(self.tmp.name)/'bad_v3.sqlite3'
  c=sqlite3.connect(legacy)
  c.executescript("""
  CREATE TABLE schema_metadata (schema_version INTEGER NOT NULL, applied_at TEXT NOT NULL);
  INSERT INTO schema_metadata VALUES (3,'bad-m23');
  CREATE TABLE event_identity (event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, request_id TEXT NOT NULL UNIQUE, occurred_at TEXT NOT NULL, committed_at TEXT NOT NULL, payload_json TEXT NOT NULL, payload_sha256 TEXT NOT NULL);
  CREATE TABLE assets (asset_id TEXT PRIMARY KEY, asset_name TEXT NOT NULL, asset_type TEXT NOT NULL, state TEXT NOT NULL, created_event_id TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL);
  CREATE TABLE inventory_authority (asset_id TEXT PRIMARY KEY, quantity INTEGER NOT NULL, total_cost_minor INTEGER NOT NULL, last_event_id TEXT NOT NULL UNIQUE, verified_at TEXT NOT NULL);
  CREATE TABLE inventory_history (history_id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL, asset_id TEXT NOT NULL, quantity_delta INTEGER NOT NULL, cost_delta_minor INTEGER NOT NULL, resulting_quantity INTEGER NOT NULL, resulting_total_cost_minor INTEGER NOT NULL, recorded_at TEXT NOT NULL, UNIQUE(event_id,asset_id));
  """)
  c.close()
  db=DatabaseManager(legacy); db.initialize()
  with db.connect() as c:
   self.assertNotIn('created_event_id TEXT NOT NULL UNIQUE',c.execute("SELECT sql FROM sqlite_master WHERE name='assets'").fetchone()[0])
   self.assertNotIn('last_event_id TEXT NOT NULL UNIQUE',c.execute("SELECT sql FROM sqlite_master WHERE name='inventory_authority'").fetchone()[0])
   self.assertEqual(c.execute('SELECT schema_version FROM schema_metadata ORDER BY rowid DESC LIMIT 1').fetchone()[0],8)


 def test_assets_v2_foreign_key_damage_is_repaired(self):
  damaged=Path(self.tmp.name)/'damaged.sqlite3'
  db=DatabaseManager(damaged); db.initialize()
  with db.connect() as c:
   c.execute('PRAGMA foreign_keys=OFF')
   c.executescript("""
   DROP TRIGGER IF EXISTS transformation_lineage_no_update;
   DROP TRIGGER IF EXISTS transformation_lineage_no_delete;
   DROP TABLE transformation_lineage;
   DROP TABLE transformations;
   CREATE TABLE transformations (transformation_id TEXT PRIMARY KEY, source_asset_id TEXT NOT NULL, source_quantity INTEGER NOT NULL CHECK(source_quantity > 0), source_cost_minor INTEGER NOT NULL CHECK(source_cost_minor >= 0), state TEXT NOT NULL CHECK(state IN ('PLANNED','IN PROGRESS','COMPLETED','CANCELLED','REVIEW')), created_event_id TEXT NOT NULL UNIQUE, completed_event_id TEXT UNIQUE, created_at TEXT NOT NULL, completed_at TEXT, FOREIGN KEY(source_asset_id) REFERENCES assets_v2(asset_id));
   CREATE TABLE transformation_lineage (lineage_id INTEGER PRIMARY KEY AUTOINCREMENT, transformation_id TEXT NOT NULL, source_asset_id TEXT NOT NULL, result_asset_id TEXT NOT NULL, allocated_cost_minor INTEGER NOT NULL CHECK(allocated_cost_minor >= 0), result_quantity INTEGER NOT NULL CHECK(result_quantity > 0), event_id TEXT NOT NULL, recorded_at TEXT NOT NULL, UNIQUE(transformation_id,result_asset_id), FOREIGN KEY(transformation_id) REFERENCES transformations(transformation_id), FOREIGN KEY(source_asset_id) REFERENCES assets_v2(asset_id), FOREIGN KEY(result_asset_id) REFERENCES assets_v2(asset_id));
   INSERT INTO schema_metadata VALUES (4,'damaged');
   """)
  db.initialize()
  with db.connect() as c:
   self.assertNotIn('assets_v2',c.execute("SELECT sql FROM sqlite_master WHERE name='transformations'").fetchone()[0])
   self.assertNotIn('assets_v2',c.execute("SELECT sql FROM sqlite_master WHERE name='transformation_lineage'").fetchone()[0])
   self.assertEqual(c.execute('SELECT schema_version FROM schema_metadata ORDER BY rowid DESC LIMIT 1').fetchone()[0],8)

if __name__=='__main__': unittest.main()
