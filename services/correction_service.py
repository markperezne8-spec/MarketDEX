from .base_service import AuthoritativeService
class CorrectionService(AuthoritativeService):
 service_name='correction_service'
 def execute(self,*,request_id,correction_event_id,original_event_id,corrective_evidence):
  if not all(str(x).strip() for x in (request_id,correction_event_id,original_event_id,corrective_evidence)): raise ValueError('Correction evidence, target, identity, and explicit request are required')
  event=self._new_event('CORRECTION',request_id,{'correction_event_id':correction_event_id,'original_event_id':original_event_id,'corrective_evidence':corrective_evidence})
  with self.database.transaction() as c:
   if c.execute('SELECT 1 FROM event_identity WHERE event_id=?',(original_event_id,)).fetchone() is None: raise ValueError('Correction target authoritative event not found')
   self._append_event_and_audit(c,event,'execute_correction')
   c.execute('INSERT INTO correction_events VALUES (?,?,?,?,?,?,?,?)',(correction_event_id,original_event_id,corrective_evidence,0,0,0,event.event_id,event.committed_at))
   c.execute('INSERT INTO event_history(event_id,original_event_id,authority_type,authority_id,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,original_event_id,'CORRECTION',correction_event_id,event.committed_at))
   c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,'CORRECTION',correction_event_id,'VERIFIED',event.committed_at))
   if c.execute('SELECT original_event_id FROM correction_events WHERE correction_event_id=?',(correction_event_id,)).fetchone()[0]!=original_event_id: raise RuntimeError('Correction lineage verification failed')
   self._verify_event(c,event)
  return event
