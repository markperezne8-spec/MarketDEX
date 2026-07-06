from .base_service import AuthoritativeService
from repositories.asset_repository import AssetRepository
VALID_STATES={'PLANNED','IN PROGRESS','COMPLETED','CANCELLED','REVIEW'}
class AssetService(AuthoritativeService):
 service_name='asset_service'
 def __init__(self,database,events,assets=None): super().__init__(database,events); self.assets=assets or AssetRepository()
 def create_asset(self,*,request_id,asset_id,asset_name,asset_type,state='PLANNED'):
  if not all(str(x).strip() for x in (request_id,asset_id,asset_name,asset_type)): raise ValueError('Asset evidence is incomplete')
  if state not in VALID_STATES: raise ValueError(f'Invalid state: {state}')
  payload={'asset_id':asset_id.strip(),'asset_name':asset_name.strip(),'asset_type':asset_type.strip(),'state':state}
  event=self._new_event('ACQUISITION',request_id,payload)
  with self.database.transaction() as c:
   self._append_event_and_audit(c,event,'create_asset')
   self.assets.insert(c,asset_id=payload['asset_id'],asset_name=payload['asset_name'],asset_type=payload['asset_type'],state=state,event_id=event.event_id,created_at=event.committed_at)
   self._verify_event(c,event)
   row=self.assets.get(c,payload['asset_id'])
   if row is None or row['created_event_id'] != event.event_id: raise RuntimeError('Post-write asset verification failed')
  return event
