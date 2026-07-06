from __future__ import annotations
import hashlib, json, uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

@dataclass(frozen=True)
class EventIdentity:
    event_id: str
    event_type: str
    request_id: str
    occurred_at: str
    committed_at: str
    payload_json: str
    payload_sha256: str

    @staticmethod
    def create(event_type: str, request_id: str, payload: dict[str, Any], occurred_at: str | None = None) -> 'EventIdentity':
        if not event_type.strip() or not request_id.strip():
            raise ValueError('event_type and request_id are required')
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        now = datetime.now(timezone.utc).isoformat()
        return EventIdentity(str(uuid.uuid4()), event_type.strip(), request_id.strip(), occurred_at or now,
                             now, payload_json, hashlib.sha256(payload_json.encode('utf-8')).hexdigest())
