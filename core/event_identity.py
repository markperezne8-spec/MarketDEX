import hashlib,json,uuid
from dataclasses import dataclass
from datetime import datetime,timezone
@dataclass(frozen=True)
class EventIdentity:
 event_id:str; event_type:str; request_id:str; occurred_at:str; committed_at:str; payload_json:str; payload_sha256:str
 @staticmethod
 def create(event_type,request_id,payload,occurred_at=None):
  if not str(event_type).strip() or not str(request_id).strip():raise ValueError('event_type and request_id are required')
  p=json.dumps(payload,sort_keys=True,separators=(',',':')); now=datetime.now(timezone.utc).isoformat(); return EventIdentity(str(uuid.uuid4()),str(event_type).strip(),str(request_id).strip(),occurred_at or now,now,p,hashlib.sha256(p.encode()).hexdigest())
