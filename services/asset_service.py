from .base_service import AuthoritativeService
class AssetService(AuthoritativeService):
 service_name='asset_service'
 def __init__(self,database,events,assets):super().__init__(database,events); self.assets=assets
 def create_asset(self,*,request_id,asset_id,asset_name,asset_type,state='PLANNED'):
  payload={'asset_id':asset_id,'asset_name':asset_name,'asset_type':asset_type,'state':state}; event=self._new_event('ACQUISITION',request_id,payload)
  with self.database.transaction() as c:self._append_event_and_audit(c,event,'create_asset'); self.assets.insert(c,asset_id=asset_id,asset_name=asset_name,asset_type=asset_type,state=state,event_id=event.event_id,created_at=event.committed_at); self._verify_event(c,event)
  return event
