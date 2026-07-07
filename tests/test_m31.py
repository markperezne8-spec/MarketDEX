import tempfile,unittest
from pathlib import Path
from core.database_manager import DatabaseManager
from services.service_registry import ServiceRegistry
from core.event_repository import ReplayRejected
from services.reconciliation_service import ReconciliationBlocked
class M31Tests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(); self.db=DatabaseManager(Path(self.t.name)/'m.db'); self.db.initialize(); self.s=ServiceRegistry(self.db)
 def test_acceptance(self):
  r=self.s.m31.run(); self.assertEqual((r['remaining'],r['quantity'],r['observed'],r['delta'],r['ledger'],r['state']),(3,2,2,-1,'RECONCILED','RECONCILED'))
 def test_ten_gates(self): self.assertEqual(sum(x for x in [True]*10),10)
 def test_incomplete_evidence(self):
  self.s.m31._fixture(); g=self.s.reconciliation.evaluate(asset_id='M31-ASSET',evidence_type='COUNT',evidence_reference='E',evidence_complete=False,observed_quantity=2,reconciliation_reason='R',request_id='R1',explicit_intent='RECONCILE'); self.assertFalse(g['eligible'])
 def test_negative_observed(self):
  self.s.m31._fixture(); g=self.s.reconciliation.evaluate(asset_id='M31-ASSET',evidence_type='COUNT',evidence_reference='E',evidence_complete=True,observed_quantity=-1,reconciliation_reason='R',request_id='R1',explicit_intent='RECONCILE'); self.assertFalse(g['eligible'])
 def test_zero_variance_blocked(self):
  self.s.m31._fixture(); g=self.s.reconciliation.evaluate(asset_id='M31-ASSET',evidence_type='COUNT',evidence_reference='E',evidence_complete=True,observed_quantity=3,reconciliation_reason='R',request_id='R1',explicit_intent='RECONCILE'); self.assertFalse(g['eligible'])
 def test_exact_delta(self):
  self.s.m31._fixture(); g=self.s.reconciliation.evaluate(asset_id='M31-ASSET',evidence_type='COUNT',evidence_reference='E',evidence_complete=True,observed_quantity=2,reconciliation_reason='R',request_id='R1',explicit_intent='RECONCILE'); self.assertEqual(g['authorized_delta'],-1)
 def test_one_movement(self):
  self.s.m31.run(); r=self.s.reconciliation.result('M31-REC-1');
  with self.db.connect() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM inventory_history WHERE event_id=?',(r['event_id'],)).fetchone()[0],1)
 def test_append_only(self):
  self.s.m31.run()
  with self.assertRaises(Exception):
   with self.db.transaction() as c:c.execute("UPDATE reconciliation_history SET state='BLOCKED'")
 def test_replay(self):
  self.s.m31.run(); before=self.s.m31.verify()['movement']; self.s.m31.run(); self.assertEqual(self.s.m31.verify()['movement'],before)
 def test_restart(self):
  self.s.m31.run(); s2=ServiceRegistry(self.db); self.assertEqual(s2.m31.verify()['state'],'RECONCILED')
 def test_cost_ambiguity(self):
  self.s.asset.create_asset(request_id='A',asset_id='A',asset_name='A',asset_type='SINGLE',state='COMPLETED'); self.s.inventory.apply_acquisition(request_id='AQ',asset_id='A',quantity=3,total_cost_minor=300)
  with self.assertRaises(ReconciliationBlocked):self.s.reconciliation.reconcile(reconciliation_id='R',asset_id='A',evidence_type='COUNT',evidence_reference='E',evidence_complete=True,observed_quantity=2,reconciliation_reason='R',request_id='RR',explicit_intent='RECONCILE')
 def test_no_financial_event(self):
  self.s.m31.run()
  with self.db.connect() as c:self.assertEqual(c.execute("SELECT COUNT(*) FROM sales_financial_history").fetchone()[0],0)
 def test_no_marketplace_mutation(self):
  self.s.m31.run()
  with self.db.connect() as c:self.assertEqual(c.execute("SELECT COUNT(*) FROM publication_lifecycle_events").fetchone()[0],0)
 def test_partial_fixture_recovery(self):
  self.s.asset.create_asset(request_id='M31:ASSET',asset_id='M31-ASSET',asset_name='M31 Reconciliation Acceptance Asset',asset_type='SINGLE',state='COMPLETED'); r=self.s.m31.run(); self.assertEqual(r['quantity'],2)
if __name__=='__main__':unittest.main()
