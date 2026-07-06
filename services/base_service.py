from __future__ import annotations
import json
from core.event_identity import EventIdentity
class AuthoritativeService:
 service_name='authoritative_service'
 def __init__(self,database,events): self.database,self.events=database,events
 def _new_event(self,event_type,request_id,payload): return EventIdentity.create(event_type,request_id,payload)
 def _append_event_and_audit(self,c,event,action_name):
  self.events.append(c,event)
  c.execute('INSERT INTO audit_history(event_id,service_name,action_name,recorded_at,detail_json) VALUES (?,?,?,?,?)',(event.event_id,self.service_name,action_name,event.committed_at,json.dumps({'request_id':event.request_id},sort_keys=True)))
 def _commit(self,event_type,request_id,payload,action_name):
  event=self._new_event(event_type,request_id,payload)
  with self.database.transaction() as c:
   self._append_event_and_audit(c,event,action_name); self._verify_event(c,event)
  return event
 def _verify_event(self,c,event):
  row=c.execute('SELECT payload_sha256 FROM event_identity WHERE event_id=?',(event.event_id,)).fetchone()
  if row is None or row['payload_sha256'] != event.payload_sha256: raise RuntimeError('Post-write event verification failed')
