import tempfile,unittest
from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import ReplayRejected
from services.service_registry import ServiceRegistry
from services.marketplace_lifecycle_service import AuthorityBlocked
class M30Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.db=DatabaseManager(Path(self.tmp.name)/'m.sqlite3'); self.db.initialize(); self.s=ServiceRegistry(self.db)
 def tearDown(self):self.tmp.cleanup()
 def runflow(self):return self.s.m30.run()
 def test_01_baseline_tables(self):
  with self.db.connect() as c:self.assertIsNotNone(c.execute("SELECT 1 FROM sqlite_master WHERE name='inventory_authority'").fetchone())
 def test_02_publication(self):self.assertEqual(self.runflow()['lifecycle']['LISTED'],2)
 def test_03_oversell(self):
  self.runflow(); self.assertEqual(self.s.m30.verify()['lifecycle']['LISTED'],2)
 def test_04_release(self):self.assertEqual(self.runflow()['lifecycle']['RELEASE'],1)
 def test_05_release_replay(self):self.assertGreaterEqual(self.runflow()['replays'],1)
 def test_06_cancel(self):self.assertEqual(self.runflow()['tcg_state'],'CANCELLED')
 def test_07_cancel_replay(self):self.assertGreaterEqual(self.runflow()['replays'],2)
 def test_08_sold_conversion(self):self.assertEqual(self.runflow()['lifecycle']['SOLD_CONVERSION'],1)
 def test_09_zero_second_decrement(self):self.assertEqual(self.runflow()['quantity'],2)
 def test_10_zero_second_financial(self):self.assertEqual(self.runflow()['financial'],1)
 def test_11_reconcile(self):
  r=self.runflow(); self.assertEqual(r['available'],r['quantity']-r['active'])
 def test_12_restart(self):
  self.runflow(); self.assertEqual(ServiceRegistry(self.db).m30.verify()['quantity'],2)
 def test_13_append_only(self):
  self.runflow()
  with self.assertRaises(Exception):
   with self.db.transaction() as c:c.execute("UPDATE publication_lifecycle_events SET quantity=9")
 def test_14_contaminated_fixture_recovery(self):
  self.s.asset.create_asset(request_id='M30:ASSET',asset_id='M30-ASSET',asset_name='M30 Publication Lifecycle Test Asset',asset_type='SINGLE',state='COMPLETED')
  r=self.runflow(); self.assertEqual((r['quantity'],r['active'],r['available']),(2,0,2))
if __name__=='__main__':unittest.main()
