from .base_service import AuthoritativeService
from repositories.asset_repository import AssetRepository
from repositories.inventory_repository import InventoryRepository
VALID_TRANSITIONS={'PLANNED':{'IN PROGRESS','CANCELLED','REVIEW'},'IN PROGRESS':{'COMPLETED','CANCELLED','REVIEW'},'REVIEW':{'IN PROGRESS','CANCELLED'},'COMPLETED':set(),'CANCELLED':set()}
class TransformationService(AuthoritativeService):
 service_name='transformation_service'
 def __init__(self,database,events,assets=None,inventory=None): super().__init__(database,events); self.assets=assets or AssetRepository(); self.inventory=inventory or InventoryRepository()
 def execute(self,*,request_id,transformation_id,source_asset_id,source_quantity,outputs):
  if not all(str(x).strip() for x in (request_id,transformation_id,source_asset_id)): raise ValueError('Transformation evidence is incomplete')
  if int(source_quantity)<=0: raise ValueError('Source quantity must be greater than zero')
  if not outputs: raise ValueError('Transformation requires explicit results')
  normalized=[]
  for o in outputs:
   if not all(str(o.get(k,'')).strip() for k in ('asset_id','asset_name','asset_type')): raise ValueError('Result evidence is incomplete')
   q=int(o.get('quantity',0)); cost=int(o.get('allocated_cost_minor',-1))
   if q<=0 or cost<0: raise ValueError('Result quantity and allocation are invalid')
   normalized.append({**o,'quantity':q,'allocated_cost_minor':cost})
  payload={'transformation_id':transformation_id,'source_asset_id':source_asset_id,'source_quantity':int(source_quantity),'outputs':normalized}
  event=self._new_event('TRANSFORMATION',request_id,payload)
  with self.database.transaction() as c:
   source=self.inventory.get(c,source_asset_id)
   if source is None or int(source['quantity'])<int(source_quantity): raise ValueError('Source inventory is unavailable')
   source_cost=int(source['total_cost_minor']) if int(source_quantity)==int(source['quantity']) else (int(source['total_cost_minor'])*int(source_quantity))//int(source['quantity'])
   if sum(o['allocated_cost_minor'] for o in normalized)!=source_cost: raise ValueError(f'Cost allocation must conserve exactly {source_cost} minor units')
   if c.execute('SELECT 1 FROM transformations WHERE transformation_id=?',(transformation_id,)).fetchone(): raise ValueError('Transformation identity already exists')
   self._append_event_and_audit(c,event,'execute_transformation')
   c.execute('INSERT INTO transformations VALUES (?,?,?,?,?,?,?,?,?)',(transformation_id,source_asset_id,int(source_quantity),source_cost,'COMPLETED',event.event_id,event.event_id,event.committed_at,event.committed_at))
   self.inventory.apply(c,asset_id=source_asset_id,quantity_delta=-int(source_quantity),cost_delta_minor=-source_cost,event_id=event.event_id,recorded_at=event.committed_at)
   for o in normalized:
    if self.assets.get(c,o['asset_id']) is not None: raise ValueError(f'Result asset already exists: {o["asset_id"]}')
    self.assets.insert(c,asset_id=o['asset_id'],asset_name=o['asset_name'].strip(),asset_type=o['asset_type'].strip().upper(),state='COMPLETED',event_id=event.event_id,created_at=event.committed_at)
    self.inventory.apply(c,asset_id=o['asset_id'],quantity_delta=o['quantity'],cost_delta_minor=o['allocated_cost_minor'],event_id=event.event_id,recorded_at=event.committed_at)
    c.execute('INSERT INTO transformation_lineage(transformation_id,source_asset_id,result_asset_id,allocated_cost_minor,result_quantity,event_id,recorded_at) VALUES (?,?,?,?,?,?,?)',(transformation_id,source_asset_id,o['asset_id'],o['allocated_cost_minor'],o['quantity'],event.event_id,event.committed_at))
   out_cost=c.execute('SELECT COALESCE(SUM(allocated_cost_minor),0) FROM transformation_lineage WHERE transformation_id=?',(transformation_id,)).fetchone()[0]
   if int(out_cost)!=source_cost: raise RuntimeError('Post-write cost conservation verification failed')
   self._verify_event(c,event)
  return event
 def validate_transition(self,current,target):
  if target not in VALID_TRANSITIONS.get(current,set()): raise ValueError(f'Invalid transformation state transition: {current} -> {target}')
  return True
