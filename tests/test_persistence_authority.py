import sqlite3,tempfile,unittest
from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository,ReplayRejected
from repositories.asset_repository import AssetRepository
from repositories.inventory_repository import InventoryRepository
from services.asset_service import AssetService
from services.inventory_service import InventoryService
class PersistenceAuthorityTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.db=DatabaseManager(Path(self.tmp.name)/'test.sqlite3'); self.db.initialize(); self.events=EventRepository(); self.assets=AssetRepository(); self.inventory=InventoryRepository(); self.asset=AssetService(self.db,self.events,self.assets); self.inv=InventoryService(self.db,self.events,self.assets,self.inventory)
 def tearDown(self): self.tmp.cleanup()
 def seed(self): self.asset.create_asset(request_id='ASSET-1',asset_id='A-1',asset_name='Test Asset',asset_type='TEST')
 def test_asset_and_acquisition_persist(self):
  self.seed(); self.inv.apply_acquisition(request_id='ACQ-1',asset_id='A-1',quantity=3,total_cost_minor=1500)
  with self.db.connect() as c:
   row=self.inventory.get(c,'A-1'); self.assertEqual((row['quantity'],row['total_cost_minor']),(3,1500)); self.assertEqual(self.inventory.history_count(c,'A-1'),1)
 def test_replay_rolls_back_second_authoritative_write(self):
  self.seed(); self.inv.apply_acquisition(request_id='ACQ-1',asset_id='A-1',quantity=3,total_cost_minor=1500)
  with self.assertRaises(ReplayRejected): self.inv.apply_acquisition(request_id='ACQ-1',asset_id='A-1',quantity=3,total_cost_minor=1500)
  with self.db.connect() as c: self.assertEqual(self.inventory.history_count(c,'A-1'),1)
 def test_negative_quantity_fails_closed(self):
  self.seed(); self.inv.apply_acquisition(request_id='ACQ-1',asset_id='A-1',quantity=1,total_cost_minor=500)
  with self.assertRaises(ValueError): self.inv.apply_movement(request_id='MOVE-1',asset_id='A-1',quantity_delta=-2,cost_delta_minor=-500)
  with self.db.connect() as c:
   row=self.inventory.get(c,'A-1'); self.assertEqual((row['quantity'],row['total_cost_minor']),(1,500)); self.assertEqual(self.events.count(c),2)
 def test_history_append_only(self):
  self.seed(); self.inv.apply_acquisition(request_id='ACQ-1',asset_id='A-1',quantity=1,total_cost_minor=500)
  with self.assertRaises(sqlite3.IntegrityError):
   with self.db.transaction() as c: c.execute('DELETE FROM inventory_history')
 def test_invalid_state_rejected(self):
  with self.assertRaises(ValueError): self.asset.create_asset(request_id='X',asset_id='A',asset_name='N',asset_type='T',state='ACTIVE')
