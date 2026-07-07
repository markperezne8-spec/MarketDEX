import tempfile,unittest
from pathlib import Path
from core.database_manager import DatabaseManager
from services.service_registry import ServiceRegistry
class M32Tests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(); self.db=DatabaseManager(Path(self.t.name)/'m.sqlite3'); self.db.initialize(); self.s=ServiceRegistry(self.db)
 def tearDown(self):self.t.cleanup()
 def test_integrated_workflow(self):self.assertEqual(self.s.m32.run()['integrity'],'OPERATIONAL INVENTORY VERIFIED')
 def test_final_quantity(self):self.s.m32.run(); self.assertEqual(self.s.m32.verify()['quantity'],2)
 def test_availability(self):self.s.m32.run(); self.assertEqual(self.s.m32.verify()['available'],2)
 def test_ledger(self):self.s.m32.run(); self.assertEqual(self.s.m32.verify()['ledger'],'RECONCILED')
 def test_replay(self):self.s.m32.run(); self.assertEqual(self.s.m32.verify()['replay'],'PASS')
 def test_restart(self):self.s.m32.run(); self.assertEqual(ServiceRegistry(self.db).m32.verify()['restart'],'PASS')
 def test_damage_capacity(self):self.s.m32.run(); self.assertEqual(self.s.m32.verify()['damage'],'VERIFIED')
 def test_loss_capacity(self):self.s.m32.run(); self.assertEqual(self.s.m32.verify()['loss'],'VERIFIED')
 def test_oversell(self):self.s.m32.run(); self.assertEqual(self.s.m32.verify()['oversell'],'BLOCKED')
 def test_release(self):self.s.m32.run(); self.assertEqual(self.s.m32.verify()['release'],'VERIFIED')
 def test_sold(self):self.s.m32.run(); self.assertEqual(self.s.m32.verify()['sold'],'VERIFIED')
 def test_reconciliation_crosscheck(self):self.s.m32.run(); self.assertEqual(self.s.m32.verify()['recon'],'VERIFIED')
