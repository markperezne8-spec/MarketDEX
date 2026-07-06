from .base_service import AuthoritativeService
from repositories.asset_repository import AssetRepository
from repositories.inventory_repository import InventoryRepository
class InventoryService(AuthoritativeService):
 service_name='inventory_service'
 def __init__(self,database,events,assets=None,inventory=None): super().__init__(database,events); self.assets=assets or AssetRepository(); self.inventory=inventory or InventoryRepository()
 def apply_acquisition(self,*,request_id,asset_id,quantity,total_cost_minor):
  if not request_id.strip() or not asset_id.strip(): raise ValueError('Acquisition evidence is incomplete')
  if not isinstance(quantity,int) or quantity <= 0: raise ValueError('Acquisition quantity must be positive')
  if not isinstance(total_cost_minor,int) or total_cost_minor < 0: raise ValueError('Acquisition cost cannot be negative')
  payload={'asset_id':asset_id,'quantity':quantity,'total_cost_minor':total_cost_minor}; event=self._new_event('ACQUISITION',request_id,payload)
  with self.database.transaction() as c:
   if self.assets.get(c,asset_id) is None: raise ValueError('Unknown asset')
   self._append_event_and_audit(c,event,'apply_acquisition')
   q,cost=self.inventory.apply(c,asset_id=asset_id,quantity_delta=quantity,cost_delta_minor=total_cost_minor,event_id=event.event_id,recorded_at=event.committed_at)
   self._verify_event(c,event); row=self.inventory.get(c,asset_id)
   if row is None or int(row['quantity'])!=q or int(row['total_cost_minor'])!=cost or row['last_event_id']!=event.event_id: raise RuntimeError('Post-write inventory verification failed')
  return event
 def apply_movement(self,*,request_id,asset_id,quantity_delta,cost_delta_minor):
  if not request_id.strip() or not asset_id.strip(): raise ValueError('Movement evidence is incomplete')
  if quantity_delta == 0 and cost_delta_minor == 0: raise ValueError('Movement must change authoritative inventory')
  payload={'asset_id':asset_id,'quantity_delta':quantity_delta,'cost_delta_minor':cost_delta_minor}; event=self._new_event('MOVEMENT',request_id,payload)
  with self.database.transaction() as c:
   if self.assets.get(c,asset_id) is None: raise ValueError('Unknown asset')
   self._append_event_and_audit(c,event,'apply_movement')
   q,cost=self.inventory.apply(c,asset_id=asset_id,quantity_delta=quantity_delta,cost_delta_minor=cost_delta_minor,event_id=event.event_id,recorded_at=event.committed_at)
   self._verify_event(c,event); row=self.inventory.get(c,asset_id)
   if int(row['quantity'])!=q or int(row['total_cost_minor'])!=cost: raise RuntimeError('Post-write inventory verification failed')
  return event
