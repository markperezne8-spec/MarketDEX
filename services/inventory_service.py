from .base_service import AuthoritativeService
class InventoryService(AuthoritativeService):
 service_name='inventory_service'
 def __init__(self,database,events,assets,inventory):super().__init__(database,events); self.assets,self.inventory=assets,inventory
 def apply_acquisition(self,*,request_id,asset_id,quantity,total_cost_minor):
  payload={'asset_id':asset_id,'quantity':int(quantity),'total_cost_minor':int(total_cost_minor)}; event=self._new_event('ACQUISITION',request_id,payload)
  with self.database.transaction() as c:
   if self.assets.get(c,asset_id) is None:raise ValueError('Unknown asset')
   self._append_event_and_audit(c,event,'apply_acquisition'); self.inventory.apply(c,asset_id=asset_id,quantity_delta=int(quantity),cost_delta_minor=int(total_cost_minor),event_id=event.event_id,recorded_at=event.committed_at); self._verify_event(c,event)
  return event

 def apply_reconciliation_delta(self,c,*,asset_id,authorized_delta,event_id,recorded_at):
  row=self.inventory.get(c,asset_id)
  if row is None: raise ValueError('Missing inventory_authority')
  delta=int(authorized_delta)
  if delta==0: raise ValueError('No reconciliation variance')
  if int(row['total_cost_minor'])!=0: raise ValueError('Cost treatment ambiguity BLOCKED')
  return self.inventory.apply(c,asset_id=asset_id,quantity_delta=delta,cost_delta_minor=0,event_id=event_id,recorded_at=recorded_at)
