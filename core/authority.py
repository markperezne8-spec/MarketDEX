import sqlite3, json, hashlib
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

SCHEMA_VERSION=11
SCHEMA='''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS meta(version INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS events(event_id TEXT PRIMARY KEY,event_type TEXT NOT NULL,request_id TEXT NOT NULL UNIQUE,payload TEXT NOT NULL,payload_sha TEXT NOT NULL,committed_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS replay_history(id INTEGER PRIMARY KEY AUTOINCREMENT,request_id TEXT NOT NULL,original_event_id TEXT NOT NULL,attempted_type TEXT NOT NULL,payload_sha TEXT NOT NULL,result TEXT NOT NULL CHECK(result='BLOCKED'),recorded_at TEXT NOT NULL,UNIQUE(request_id,attempted_type,payload_sha));
CREATE TABLE IF NOT EXISTS assets(asset_id TEXT PRIMARY KEY,name TEXT NOT NULL,created_event_id TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS inventory(asset_id TEXT PRIMARY KEY,quantity INTEGER NOT NULL CHECK(quantity>=0),total_cost_minor INTEGER NOT NULL CHECK(total_cost_minor>=0),last_event_id TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS inventory_history(id INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT NOT NULL,asset_id TEXT NOT NULL,quantity_delta INTEGER NOT NULL,cost_delta_minor INTEGER NOT NULL,resulting_quantity INTEGER NOT NULL,resulting_cost_minor INTEGER NOT NULL,recorded_at TEXT NOT NULL,UNIQUE(event_id,asset_id));
CREATE TABLE IF NOT EXISTS sales(sale_id TEXT PRIMARY KEY,asset_id TEXT NOT NULL,marketplace TEXT NOT NULL,quantity INTEGER NOT NULL CHECK(quantity>0),revenue_minor INTEGER NOT NULL,fees_minor INTEGER NOT NULL,shipping_minor INTEGER NOT NULL,packaging_minor INTEGER NOT NULL,cogs_minor INTEGER NOT NULL,profit_minor INTEGER NOT NULL,event_id TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sale_financial_history(id INTEGER PRIMARY KEY AUTOINCREMENT,sale_id TEXT NOT NULL,event_id TEXT NOT NULL UNIQUE,profit_minor INTEGER NOT NULL,recorded_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS marketplace_allocations(allocation_id TEXT PRIMARY KEY,asset_id TEXT NOT NULL,marketplace TEXT NOT NULL,publication_reference TEXT NOT NULL,publication_identity TEXT NOT NULL,requested_quantity INTEGER NOT NULL CHECK(requested_quantity>0),allocated_quantity INTEGER NOT NULL CHECK(allocated_quantity>0),released_quantity INTEGER NOT NULL DEFAULT 0,cancelled_quantity INTEGER NOT NULL DEFAULT 0,consumed_quantity INTEGER NOT NULL DEFAULT 0,state TEXT NOT NULL CHECK(state IN ('PLANNED','ACTIVE','RELEASED','CANCELLED','CONSUMED')),source_event_id TEXT NOT NULL,created_at TEXT NOT NULL,committed_at TEXT NOT NULL,verified_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS publication_lifecycle_events(lifecycle_id TEXT PRIMARY KEY,allocation_id TEXT NOT NULL,event_type TEXT NOT NULL CHECK(event_type IN ('LISTED','RELEASE','CANCELLATION','SOLD_CONVERSION')),quantity INTEGER NOT NULL CHECK(quantity>=0),evidence_type TEXT NOT NULL,evidence_reference TEXT NOT NULL,evidence_complete INTEGER NOT NULL CHECK(evidence_complete=1),marketplace TEXT NOT NULL,publication_reference TEXT,publication_identity TEXT,sale_id TEXT,sale_event_id TEXT,source_event_id TEXT,event_id TEXT NOT NULL UNIQUE,request_id TEXT NOT NULL UNIQUE,replay_key TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL,committed_at TEXT NOT NULL,verified_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audits(id INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT NOT NULL,authority_type TEXT NOT NULL,authority_id TEXT NOT NULL,result TEXT NOT NULL CHECK(result='VERIFIED'),recorded_at TEXT NOT NULL,UNIQUE(event_id,authority_type,authority_id));
CREATE TABLE IF NOT EXISTS exceptions(exception_id TEXT PRIMARY KEY,exception_type TEXT NOT NULL,evidence TEXT NOT NULL,state TEXT NOT NULL CHECK(state IN ('REVIEW','COMPLETED')),event_id TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL);
CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT,'events immutable'); END;
CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT,'events immutable'); END;
CREATE TRIGGER IF NOT EXISTS inventory_history_no_update BEFORE UPDATE ON inventory_history BEGIN SELECT RAISE(ABORT,'inventory history append-only'); END;
CREATE TRIGGER IF NOT EXISTS inventory_history_no_delete BEFORE DELETE ON inventory_history BEGIN SELECT RAISE(ABORT,'inventory history append-only'); END;
CREATE TRIGGER IF NOT EXISTS lifecycle_no_update BEFORE UPDATE ON publication_lifecycle_events BEGIN SELECT RAISE(ABORT,'publication lifecycle append-only'); END;
CREATE TRIGGER IF NOT EXISTS lifecycle_no_delete BEFORE DELETE ON publication_lifecycle_events BEGIN SELECT RAISE(ABORT,'publication lifecycle append-only'); END;
CREATE TRIGGER IF NOT EXISTS audits_no_update BEFORE UPDATE ON audits BEGIN SELECT RAISE(ABORT,'audit append-only'); END;
CREATE TRIGGER IF NOT EXISTS audits_no_delete BEFORE DELETE ON audits BEGIN SELECT RAISE(ABORT,'audit append-only'); END;
'''

def now(): return datetime.now(timezone.utc).isoformat()
def canonical(payload): return json.dumps(payload,sort_keys=True,separators=(',',':'))
def digest(payload): return hashlib.sha256(canonical(payload).encode()).hexdigest()
class ReplayRejected(RuntimeError): pass
class AuthorityBlocked(ValueError): pass

class Database:
 def __init__(self,path): self.path=Path(path)
 def initialize(self):
  self.path.parent.mkdir(parents=True,exist_ok=True)
  with self.connect() as c:
   c.executescript(SCHEMA)
   if c.execute('SELECT COUNT(*) FROM meta').fetchone()[0]==0: c.execute('INSERT INTO meta VALUES (?)',(SCHEMA_VERSION,))
   else: c.execute('UPDATE meta SET version=?',(SCHEMA_VERSION,))
 def connect(self):
  c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c
 @contextmanager
 def transaction(self):
  c=self.connect()
  try: c.execute('BEGIN IMMEDIATE'); yield c; c.commit()
  except ReplayRejected:
   c.commit(); raise
  except:
   c.rollback(); raise
  finally: c.close()

class Authority:
 def __init__(self,db): self.db=db
 def event(self,c,event_type,request_id,payload):
  if not str(request_id).strip(): raise AuthorityBlocked('unknown request identity')
  p=canonical(payload); h=digest(payload); existing=c.execute('SELECT * FROM events WHERE request_id=?',(request_id,)).fetchone()
  if existing:
   try: c.execute('INSERT INTO replay_history(request_id,original_event_id,attempted_type,payload_sha,result,recorded_at) VALUES (?,?,?,?,?,?)',(request_id,existing['event_id'],event_type,h,'BLOCKED',now()))
   except sqlite3.IntegrityError: pass
   raise ReplayRejected('Request already committed — ZERO second authoritative mutation')
  eid=f'EVT-{uuid4()}'; ts=now(); c.execute('INSERT INTO events VALUES (?,?,?,?,?,?)',(eid,event_type,request_id,p,h,ts)); return eid,ts
 def reject_replay(self,c,event_type,request_id,payload):
  existing=c.execute('SELECT * FROM events WHERE request_id=?',(request_id,)).fetchone()
  if existing:
   h=digest(payload)
   try:c.execute('INSERT INTO replay_history(request_id,original_event_id,attempted_type,payload_sha,result,recorded_at) VALUES (?,?,?,?,?,?)',(request_id,existing['event_id'],event_type,h,'BLOCKED',now()))
   except sqlite3.IntegrityError:pass
   raise ReplayRejected('Request already committed — ZERO second authoritative mutation')

 def audit(self,c,eid,typ,aid,ts): c.execute('INSERT INTO audits(event_id,authority_type,authority_id,result,recorded_at) VALUES (?,?,?,?,?)',(eid,typ,aid,'VERIFIED',ts))
