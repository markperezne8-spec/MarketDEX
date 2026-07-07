import sqlite3
class ReplayRejected(RuntimeError):pass
class EventRepository:
 def append(self,c,event):
  try:c.execute('INSERT INTO event_identity(event_id,event_type,request_id,occurred_at,committed_at,payload_json,payload_sha256) VALUES (?,?,?,?,?,?,?)',tuple(event.__dict__.values()))
  except sqlite3.IntegrityError as exc:raise ReplayRejected(f'Request already committed: {event.request_id}') from exc
