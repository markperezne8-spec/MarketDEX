import sqlite3,tempfile,unittest
from pathlib import Path
from core.database_manager import DatabaseManager
from services.service_registry import ServiceRegistry
class M25AuthorityTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)/'m.sqlite3'; self.db=DatabaseManager(self.path); self.db.initialize(); self.s=ServiceRegistry(self.db)
  self.s.asset.create_asset(request_id='a',asset_id='PACK',asset_name='Pack',asset_type='PACK',state='COMPLETED'); self.s.inventory.apply_acquisition(request_id='i',asset_id='PACK',quantity=6,total_cost_minor=6000)
  self.s.sales.record_sale(request_id='sale',sale_id='S1',asset_id='PACK',quantity=2,revenue_minor=3000,marketplace_fees_minor=300,shipping_minor=500,packaging_minor=100)
  with self.db.connect() as c: self.sale_event=c.execute("SELECT created_event_id FROM sales WHERE sale_id='S1'").fetchone()[0]
 def tearDown(self): self.tmp.cleanup()
 def ret(self,request='ret'): return self.s.return_service.execute(request_id=request,return_id='R1',sale_id='S1',quantity=2,condition_evidence='SEALED VERIFIED',restock_authorized=True,refund_minor=3000)
 def test_return_chain_inventory_cost_financial_profit(self):
  self.ret()
  with self.db.connect() as c:
   inv=c.execute("SELECT * FROM inventory_authority WHERE asset_id='PACK'").fetchone(); r=c.execute("SELECT * FROM returns WHERE return_id='R1'").fetchone()
   self.assertEqual((inv['quantity'],inv['total_cost_minor']),(6,6000)); self.assertEqual(r['restored_cost_minor'],2000); self.assertEqual(r['profit_restatement_minor'],-1000)
   self.assertEqual(c.execute("SELECT original_event_id FROM return_events WHERE return_id='R1'").fetchone()[0],self.sale_event)
   self.assertEqual(c.execute("SELECT amount_minor FROM financial_events").fetchone()[0],-3000)
 def test_no_condition_no_write(self):
  with self.assertRaises(ValueError): self.s.return_service.execute(request_id='x',return_id='R',sale_id='S1',quantity=1,condition_evidence='',restock_authorized=True,refund_minor=100)
  with self.db.connect() as c: self.assertEqual(c.execute('SELECT COUNT(*) FROM returns').fetchone()[0],0)
 def test_no_restock_zero_cost_restoration(self):
  self.s.return_service.execute(request_id='x',return_id='R',sale_id='S1',quantity=1,condition_evidence='DAMAGED',restock_authorized=False,refund_minor=1000)
  with self.db.connect() as c: self.assertEqual(c.execute("SELECT restored_cost_minor FROM returns").fetchone()[0],0); self.assertEqual(c.execute("SELECT quantity FROM inventory_authority WHERE asset_id='PACK'").fetchone()[0],4)
 def test_unmatched_sale_fails_closed(self):
  with self.assertRaises(ValueError): self.s.return_service.execute(request_id='x',return_id='R',sale_id='NO',quantity=1,condition_evidence='OK',restock_authorized=True,refund_minor=1)
 def test_correction_append_only_original_immutable(self):
  before=self._event_hash(self.sale_event); self.s.correction.execute(request_id='c',correction_event_id='C1',original_event_id=self.sale_event,corrective_evidence='verified')
  self.assertEqual(before,self._event_hash(self.sale_event))
  with self.db.connect() as c: self.assertEqual(c.execute("SELECT original_event_id FROM correction_events").fetchone()[0],self.sale_event)
 def test_reversal_append_only_original_immutable(self):
  before=self._event_hash(self.sale_event); self.s.reversal.execute(request_id='v',reversal_event_id='V1',original_event_id=self.sale_event); self.assertEqual(before,self._event_hash(self.sale_event))
 def test_return_replay_zero_second_mutation(self):
  self.ret()
  with self.db.connect() as c: before=(c.execute("SELECT quantity,total_cost_minor FROM inventory_authority WHERE asset_id='PACK'").fetchone()[:],c.execute('SELECT COUNT(*) FROM financial_events').fetchone()[0])
  with self.assertRaises(Exception): self.s.return_service.execute(request_id='ret',return_id='R2',sale_id='S1',quantity=2,condition_evidence='SEALED VERIFIED',restock_authorized=True,refund_minor=3000)
  with self.db.connect() as c: after=(c.execute("SELECT quantity,total_cost_minor FROM inventory_authority WHERE asset_id='PACK'").fetchone()[:],c.execute('SELECT COUNT(*) FROM financial_events').fetchone()[0])
  self.assertEqual(before,after)
 def test_correction_and_reversal_replay_zero_second_mutation(self):
  self.s.correction.execute(request_id='c',correction_event_id='C1',original_event_id=self.sale_event,corrective_evidence='verified')
  with self.assertRaises(Exception): self.s.correction.execute(request_id='c',correction_event_id='C2',original_event_id=self.sale_event,corrective_evidence='verified')
  self.s.reversal.execute(request_id='v',reversal_event_id='V1',original_event_id=self.sale_event)
  with self.assertRaises(Exception): self.s.reversal.execute(request_id='v',reversal_event_id='V2',original_event_id=self.sale_event)
  with self.db.connect() as c: self.assertEqual(c.execute('SELECT COUNT(*) FROM correction_events').fetchone()[0],1); self.assertEqual(c.execute('SELECT COUNT(*) FROM reversal_events').fetchone()[0],1)
 def test_persistence_restart_complete_chain(self):
  self.ret(); self.s.correction.execute(request_id='c',correction_event_id='C1',original_event_id=self.sale_event,corrective_evidence='verified'); self.s.reversal.execute(request_id='v',reversal_event_id='V1',original_event_id=self.sale_event)
  db2=DatabaseManager(self.path); db2.initialize()
  with db2.connect() as c: self.assertEqual((c.execute('SELECT COUNT(*) FROM returns').fetchone()[0],c.execute('SELECT COUNT(*) FROM correction_events').fetchone()[0],c.execute('SELECT COUNT(*) FROM reversal_events').fetchone()[0]),(1,1,1))
 def test_history_tables_append_only(self):
  self.ret()
  for table in ('return_events','inventory_movements','financial_events','event_history','audit_events'):
   with self.assertRaises(sqlite3.IntegrityError):
    with self.db.transaction() as c: c.execute(f'DELETE FROM {table}')
 def _event_hash(self,eid):
  with self.db.connect() as c: return c.execute("SELECT payload_sha256 FROM event_identity WHERE event_id=?",(eid,)).fetchone()[0]
if __name__=='__main__': unittest.main()
