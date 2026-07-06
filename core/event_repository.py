from __future__ import annotations
import sqlite3
from .event_identity import EventIdentity

class ReplayRejected(RuntimeError): pass

class EventRepository:
    def append(self, connection: sqlite3.Connection, event: EventIdentity) -> None:
        try:
            connection.execute('''INSERT INTO event_identity
                (event_id,event_type,request_id,occurred_at,committed_at,payload_json,payload_sha256)
                VALUES (?,?,?,?,?,?,?)''', tuple(event.__dict__.values()))
        except sqlite3.IntegrityError as exc:
            raise ReplayRejected(f'Request already committed: {event.request_id}') from exc

    def count(self, connection: sqlite3.Connection) -> int:
        return int(connection.execute('SELECT COUNT(*) FROM event_identity').fetchone()[0])
