import tempfile, unittest
from pathlib import Path
from core.database_manager import DatabaseManager
from services.service_registry import ServiceRegistry
class WorkflowTests(unittest.TestCase):
 def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.db=DatabaseManager(Path(self.tmp.name)/'m.sqlite3'); self.db.initialize(); self.s=ServiceRegistry(self.db)
 def tearDown(self): self.tmp.cleanup()
 def test_asset_acquisition_persists_and_history_explains_result(self):
  self.s.asset.create_asset(request_id='r-a',asset_id='A-001',asset_name='Test Asset',asset_type='SINGLE',state='PLANNED'); self.s.inventory.apply_acquisition(request_id='r-i',asset_id='A-001',quantity=3,total_cost_minor=1500)
  with self.db.connect() as c:
   row=c.execute('SELECT * FROM inventory_authority WHERE asset_id=?',('A-001',)).fetchone(); self.assertEqual((row['quantity'],row['total_cost_minor']),(3,1500)); self.assertEqual(c.execute('SELECT COUNT(*) FROM inventory_history WHERE asset_id=?',('A-001',)).fetchone()[0],1); self.assertEqual(c.execute('SELECT COUNT(*) FROM event_identity').fetchone()[0],2)
 def test_incomplete_evidence_fails_closed(self):
  with self.assertRaises(ValueError): self.s.asset.create_asset(request_id='r',asset_id='',asset_name='X',asset_type='SINGLE')
  with self.db.connect() as c: self.assertEqual(c.execute('SELECT COUNT(*) FROM assets').fetchone()[0],0)
 def test_duplicate_asset_rolls_back_second_event(self):
  self.s.asset.create_asset(request_id='r1',asset_id='A',asset_name='X',asset_type='SINGLE')
  with self.assertRaises(Exception): self.s.asset.create_asset(request_id='r2',asset_id='A',asset_name='X',asset_type='SINGLE')
  with self.db.connect() as c: self.assertEqual(c.execute('SELECT COUNT(*) FROM event_identity').fetchone()[0],1)
if __name__=='__main__': unittest.main()
