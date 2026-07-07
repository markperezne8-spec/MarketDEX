from .base_service import AuthoritativeService
class ReversalService(AuthoritativeService):
 service_name='reversal_service'
 def execute(self,*,request_id,reversal_event_id,original_event_id):
  if not all(str(x).strip() for x in (request_id,reversal_event_id,original_event_id)): raise ValueError('Reversal identity, original event, and explicit request are required')
  event=self._new_event('REVERSAL',request_id,{'reversal_event_id':reversal_event_id,'original_event_id':original_event_id})
  with self.database.transaction() as c:
   if c.execute('SELECT 1 FROM event_identity WHERE event_id=?',(original_event_id,)).fetchone() is None: raise ValueError('Original authoritative event not found')
   self._append_event_and_audit(c,event,'execute_reversal')
   c.execute('INSERT INTO reversal_events VALUES (?,?,?,?,?,?,?)',(reversal_event_id,original_event_id,0,0,0,event.event_id,event.committed_at))
   c.execute('INSERT INTO event_history(event_id,original_event_id,authority_type,authority_id,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,original_event_id,'REVERSAL',reversal_event_id,event.committed_at))
   c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,'REVERSAL',reversal_event_id,'VERIFIED',event.committed_at))
   if c.execute('SELECT original_event_id FROM reversal_events WHERE reversal_event_id=?',(reversal_event_id,)).fetchone()[0]!=original_event_id: raise RuntimeError('Reversal lineage verification failed')
   self._verify_event(c,event)
  return event
