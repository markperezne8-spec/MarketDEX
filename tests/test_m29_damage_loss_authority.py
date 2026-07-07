import tempfile,unittest
from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import ReplayRejected
from services.service_registry import ServiceRegistry

class M29Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)/'m.sqlite3'; self.db=DatabaseManager(self.path); self.db.initialize(); self.s=ServiceRegistry(self.db)
  self.s.asset.create_asset(request_id='a',asset_id='A',asset_name='A',asset_type='SINGLE',state='COMPLETED'); self.s.inventory.apply_acquisition(request_id='i',asset_id='A',quantity=3,total_cost_minor=300)
 def tearDown(self): self.tmp.cleanup()
 def args(self,typ='DAMAGE',q=1,req='d',ref='e',complete=True,aid='ADJ'):
  return dict(request_id=req,adjustment_id=aid,asset_id='A',adjustment_type=typ,adjustment_quantity=q,evidence_type='PHOTO',evidence_reference=ref,evidence_complete=complete)
 def test_incomplete_evidence_zero_write(self):
  g=self.s.adjustment.eligibility(asset_id='A',adjustment_type='DAMAGE',adjustment_quantity=1,evidence_type='PHOTO',evidence_reference='',evidence_complete=False,request_id='x'); self.assertFalse(g['adjustment_eligible'])
  with self.assertRaises(ValueError): self.s.adjustment.execute(**self.args(ref='',complete=False))
  with self.db.connect() as c:self.assertEqual(c.execute("SELECT COUNT(*) FROM inventory_movements WHERE movement_type='DAMAGE'").fetchone()[0],0)
 def test_damage_and_loss_append_negative_movements(self):
  self.s.adjustment.execute(**self.args())
  self.s.adjustment.execute(**self.args(typ='LOSS',req='l',aid='L'))
  with self.db.connect() as c:
   self.assertEqual(c.execute("SELECT quantity FROM inventory_authority WHERE asset_id='A'").fetchone()[0],1)
   self.assertEqual([r[0] for r in c.execute("SELECT quantity_delta FROM inventory_movements WHERE movement_type IN ('DAMAGE','LOSS') ORDER BY recorded_at")],[-1,-1])
 def test_exceeds_available_fails_closed(self):
  with self.assertRaises(ValueError):self.s.adjustment.execute(**self.args(typ='LOSS',q=4))
 def test_active_allocation_reduces_available(self):
  self.s.integration.allocate(request_id='x',allocation_id='X',asset_id='A',marketplace='EBAY',allocated_quantity=2,publication_reference='P')
  self.assertEqual(self.s.adjustment.available_quantity('A'),1)
  with self.assertRaises(ValueError):self.s.adjustment.execute(**self.args(q=2))
 def test_replay_zero_second_decrement(self):
  self.s.adjustment.execute(**self.args())
  with self.assertRaises(ReplayRejected):self.s.adjustment.execute(**self.args(aid='OTHER'))
  with self.db.connect() as c:self.assertEqual(c.execute("SELECT quantity FROM inventory_authority WHERE asset_id='A'").fetchone()[0],2)
 def test_restart_replay_persists(self):
  self.s.adjustment.execute(**self.args())
  db2=DatabaseManager(self.path); db2.initialize(); s2=ServiceRegistry(db2)
  with self.assertRaises(ReplayRejected):s2.adjustment.execute(**self.args(aid='OTHER'))
  with db2.connect() as c:self.assertEqual(c.execute("SELECT quantity FROM inventory_authority WHERE asset_id='A'").fetchone()[0],2)
 def test_ledger_reconciles(self):
  self.s.adjustment.execute(**self.args())
  with self.db.connect() as c:
   q=c.execute("SELECT quantity FROM inventory_authority WHERE asset_id='A'").fetchone()[0]; expected=c.execute("SELECT SUM(quantity_delta) FROM inventory_history WHERE asset_id='A'").fetchone()[0]
  self.assertEqual(q,expected)
 def test_append_only_adjustment_authority(self):
  self.s.adjustment.execute(**self.args())
  with self.db.connect() as c:
   with self.assertRaises(Exception):c.execute("UPDATE inventory_adjustments SET control_result='BLOCKED'")
 def test_exact_acceptance_chain(self):
  r=self.s.m29.run()
  self.assertEqual((r['quantity'],r['damage'],r['loss'],r['movements'],r['audits']),(1,1,1,2,2)); self.assertTrue(r['reconciled'])
if __name__=='__main__':unittest.main()
