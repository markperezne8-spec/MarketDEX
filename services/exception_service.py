from .base_service import AuthoritativeService
class ExceptionService(AuthoritativeService):
 service_name='exception_service'
 def record(self,*,request_id,exception_id,exception_type,evidence,source_event_id=None):
  if not all(str(x).strip() for x in (request_id,exception_id,exception_type,evidence)):
   raise ValueError('Exception identity and evidence are required')
  payload={'exception_id':exception_id,'exception_type':exception_type,'evidence':evidence,'source_event_id':source_event_id}
  event=self._new_event('EXCEPTION',request_id,payload)
  with self.database.transaction() as c:
   if source_event_id and c.execute('SELECT 1 FROM event_identity WHERE event_id=?',(source_event_id,)).fetchone() is None:
    raise ValueError('Exception source authoritative event not found')
   self._append_event_and_audit(c,event,'record_exception')
   c.execute('INSERT INTO exception_authority VALUES (?,?,?,?,?,?,?)',(exception_id,source_event_id,exception_type,evidence,'REVIEW',event.event_id,event.committed_at))
   c.execute('INSERT INTO exception_history(exception_id,event_id,source_event_id,exception_type,evidence,state,recorded_at) VALUES (?,?,?,?,?,?,?)',(exception_id,event.event_id,source_event_id,exception_type,evidence,'REVIEW',event.committed_at))
   row=c.execute('SELECT event_id,evidence,state FROM exception_authority WHERE exception_id=?',(exception_id,)).fetchone()
   if row is None or row['event_id']!=event.event_id or row['evidence']!=evidence or row['state']!='REVIEW':
    raise RuntimeError('Exception post-write verification failed')
   self._verify_event(c,event)
  return event
