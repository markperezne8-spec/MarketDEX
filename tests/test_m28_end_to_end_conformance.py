import tempfile,unittest
from pathlib import Path
from core.database_manager import DatabaseManager
from services.service_registry import ServiceRegistry

class M28EndToEndConformanceTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)/'m.sqlite3'; self.db=DatabaseManager(self.path); self.db.initialize(); self.s=ServiceRegistry(self.db)
 def tearDown(self): self.tmp.cleanup()
 def test_complete_authority_chain(self):
  r=self.s.conformance.run_clean_acceptance(); self.assertTrue(r['oversell_blocked'])
  with self.db.connect() as c:
   self.assertEqual(c.execute('SELECT COUNT(*) FROM marketplace_allocations').fetchone()[0],1)
   self.assertEqual(c.execute('SELECT COUNT(*) FROM order_closures').fetchone()[0],1)
   self.assertEqual(c.execute('SELECT COUNT(*) FROM exception_resolutions').fetchone()[0],1)
   self.assertEqual(c.execute("SELECT state FROM exception_authority").fetchone()[0],'COMPLETED')
 def test_cross_channel_oversell_fails_closed(self):
  self.s.asset.create_asset(request_id='a',asset_id='A',asset_name='A',asset_type='SINGLE',state='COMPLETED'); self.s.inventory.apply_acquisition(request_id='i',asset_id='A',quantity=3,total_cost_minor=300)
  self.s.integration.allocate(request_id='x',allocation_id='X',asset_id='A',marketplace='EBAY',allocated_quantity=2,publication_reference='P')
  with self.assertRaises(ValueError): self.s.integration.allocate(request_id='y',allocation_id='Y',asset_id='A',marketplace='TCGPLAYER',allocated_quantity=2,publication_reference='Q')
  with self.db.connect() as c: self.assertEqual(c.execute('SELECT COUNT(*) FROM marketplace_allocations').fetchone()[0],1)
 def test_settlement_must_match_net_proceeds(self):
  self.s.asset.create_asset(request_id='a',asset_id='A',asset_name='A',asset_type='SINGLE',state='COMPLETED'); self.s.inventory.apply_acquisition(request_id='i',asset_id='A',quantity=1,total_cost_minor=100)
  self.s.sales.record_sale(request_id='s',sale_id='S',asset_id='A',quantity=1,revenue_minor=1000,marketplace_fees_minor=100,shipping_minor=100,packaging_minor=100)
  with self.assertRaises(ValueError): self.s.integration.settle_and_close(request_id='c',settlement_reference='SET',sale_id='S',settled_minor=701)
 def test_no_variance_no_exception(self):
  self.s.asset.create_asset(request_id='a',asset_id='A',asset_name='A',asset_type='SINGLE',state='COMPLETED'); self.s.inventory.apply_acquisition(request_id='i',asset_id='A',quantity=1,total_cost_minor=100)
  with self.assertRaises(ValueError): self.s.integration.detect_variance(request_id='v',exception_id='E',asset_id='A',expected_quantity=1)
 def test_resolution_requires_unresolved_exception(self):
  with self.assertRaises(ValueError): self.s.integration.resolve_exception(request_id='r',resolution_event_id='R',exception_id='missing',evidence='explicit')
 def test_replay_sale_return_correction_resolution_zero_second_mutation(self):
  r=self.s.conformance.run_clean_acceptance(); op=r['operation']; pack=r['pack']
  with self.db.connect() as c:
   before=(c.execute('SELECT quantity,total_cost_minor FROM inventory_authority WHERE asset_id=?',(pack,)).fetchone()[:],
           c.execute('SELECT COUNT(*) FROM sales_financial_history').fetchone()[0],
           c.execute('SELECT COUNT(*) FROM financial_events').fetchone()[0],
           c.execute('SELECT COUNT(*) FROM correction_events').fetchone()[0],
           c.execute('SELECT COUNT(*) FROM exception_resolutions').fetchone()[0])
  calls=[
   lambda:self.s.sales.record_sale(request_id=f'{op}:sale',sale_id='S2',asset_id=pack,quantity=2,revenue_minor=3000,marketplace_fees_minor=300,shipping_minor=500,packaging_minor=100),
   lambda:self.s.return_service.execute(request_id=f'{op}:return',return_id='R2',sale_id=f'SALE-{op}',quantity=2,condition_evidence='SEALED VERIFIED',restock_authorized=True,refund_minor=3000),
   lambda:self.s.correction.execute(request_id=f'{op}:correction',correction_event_id='C2',original_event_id=self._sale_event(op),corrective_evidence='x'),
   lambda:self.s.integration.resolve_exception(request_id=f'{op}:resolution',resolution_event_id='R2',exception_id=f'EXC-{op}',evidence='x')]
  for call in calls:
   with self.assertRaises(Exception): call()
  with self.db.connect() as c:
   after=(c.execute('SELECT quantity,total_cost_minor FROM inventory_authority WHERE asset_id=?',(pack,)).fetchone()[:],
          c.execute('SELECT COUNT(*) FROM sales_financial_history').fetchone()[0],
          c.execute('SELECT COUNT(*) FROM financial_events').fetchone()[0],
          c.execute('SELECT COUNT(*) FROM correction_events').fetchone()[0],
          c.execute('SELECT COUNT(*) FROM exception_resolutions').fetchone()[0])
  self.assertEqual(before,after)
 def test_restart_and_dashboard_zero_writes(self):
  self.s.conformance.run_clean_acceptance(); before=self.s.dashboard.mission_control()
  with self.db.connect() as c: event_count=c.execute('SELECT COUNT(*) FROM event_identity').fetchone()[0]
  db2=DatabaseManager(self.path); db2.initialize(); s2=ServiceRegistry(db2); after=s2.dashboard.mission_control(); s2.dashboard.recent_authority()
  with db2.connect() as c: after_events=c.execute('SELECT COUNT(*) FROM event_identity').fetchone()[0]
  self.assertEqual(before,after); self.assertEqual(event_count,after_events)
 def _sale_event(self,op):
  with self.db.connect() as c:return c.execute('SELECT created_event_id FROM sales WHERE sale_id=?',(f'SALE-{op}',)).fetchone()[0]
if __name__=='__main__':unittest.main()
