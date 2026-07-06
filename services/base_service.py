from __future__ import annotations
import json
from core.database_manager import DatabaseManager
from core.event_identity import EventIdentity
from core.event_repository import EventRepository

class AuthoritativeService:
    service_name = 'authoritative_service'
    def __init__(self, database: DatabaseManager, events: EventRepository):
        self.database, self.events = database, events

    def _commit(self, event_type: str, request_id: str, payload: dict, action_name: str) -> EventIdentity:
        event = EventIdentity.create(event_type, request_id, payload)
        with self.database.transaction() as connection:
            self.events.append(connection, event)
            connection.execute('INSERT INTO audit_history(event_id,service_name,action_name,recorded_at,detail_json) VALUES (?,?,?,?,?)',
                               (event.event_id, self.service_name, action_name, event.committed_at,
                                json.dumps({'request_id': request_id}, sort_keys=True)))
        return event
