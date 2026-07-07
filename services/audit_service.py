from .base_service import AuthoritativeService
class AuditService(AuthoritativeService):
 service_name='audit_service'
 def verify(self,*,request_id,audit_verification_id,target_event_id):
  if not all(str(x).strip() for x in (request_id,audit_verification_id,target_event_id)):
   raise ValueError('Audit target, identity, and explicit request are required')
  with self.database.connect() as c:
   target=c.execute('SELECT payload_sha256 FROM event_identity WHERE event_id=?',(target_event_id,)).fetchone()
  if target is None: raise ValueError('Audit target authoritative event not found')
  expected=target['payload_sha256']
  event=self._new_event('AUDIT_VERIFICATION',request_id,{'audit_verification_id':audit_verification_id,'target_event_id':target_event_id,'target_payload_sha256':expected})
  with self.database.transaction() as c:
   current=c.execute('SELECT payload_sha256 FROM event_identity WHERE event_id=?',(target_event_id,)).fetchone()
   result='VERIFIED' if current and current['payload_sha256']==expected else 'FAILED'
   self._append_event_and_audit(c,event,'verify_authoritative_event')
   c.execute('INSERT INTO audit_verifications VALUES (?,?,?,?,?,?)',(audit_verification_id,target_event_id,expected,result,event.event_id,event.committed_at))
   self._verify_event(c,event)
   saved=c.execute('SELECT verification_result FROM audit_verifications WHERE audit_verification_id=?',(audit_verification_id,)).fetchone()
   if saved is None or saved['verification_result']!=result: raise RuntimeError('Audit post-write verification failed')
  return event,result
