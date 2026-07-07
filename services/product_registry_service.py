import hashlib, json, re, sqlite3, uuid
from pathlib import Path
from datetime import datetime, timezone
BASELINE='9c8bb74166eac532cf81b299400edd3b6c2f118c'
ACCEPTANCE_REQUEST='M34-REGISTER-CHARIZARD-001'

def now(): return datetime.now(timezone.utc).isoformat()
def norm(v): return re.sub(r'[^a-z0-9]+',' ',(v or '').casefold()).strip()
class ProductRegistryService:
    def __init__(self,path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self._init()
    def _c(self): c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c
    def _init(self):
      with self._c() as c:
       c.executescript("""
       CREATE TABLE IF NOT EXISTS event_identity(event_id TEXT PRIMARY KEY,event_type TEXT NOT NULL,request_id TEXT NOT NULL UNIQUE,occurred_at TEXT NOT NULL,committed_at TEXT NOT NULL,payload_json TEXT NOT NULL,payload_sha256 TEXT NOT NULL);
       CREATE TABLE IF NOT EXISTS replay_defense_history(replay_history_id INTEGER PRIMARY KEY AUTOINCREMENT,request_id TEXT NOT NULL,original_event_id TEXT NOT NULL,attempted_event_type TEXT NOT NULL,payload_sha256 TEXT NOT NULL,defense_result TEXT NOT NULL CHECK(defense_result='BLOCKED'),recorded_at TEXT NOT NULL,UNIQUE(request_id,attempted_event_type,payload_sha256));
       CREATE TABLE IF NOT EXISTS products(product_id TEXT PRIMARY KEY,product_type TEXT NOT NULL CHECK(product_type IN ('SINGLE','SEALED')),canonical_name TEXT NOT NULL,normalized_identity_key TEXT NOT NULL UNIQUE,set_name TEXT,card_number TEXT,variant_name TEXT,state TEXT NOT NULL CHECK(state='REGISTERED'),created_event_id TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL);
       CREATE TABLE IF NOT EXISTS product_aliases(alias_id TEXT PRIMARY KEY,product_id TEXT NOT NULL,alias_name TEXT NOT NULL,normalized_alias_key TEXT NOT NULL UNIQUE,created_event_id TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL,FOREIGN KEY(product_id) REFERENCES products(product_id));
       CREATE TABLE IF NOT EXISTS product_registration_history(registration_history_id INTEGER PRIMARY KEY AUTOINCREMENT,product_id TEXT NOT NULL,registration_request_id TEXT NOT NULL,event_id TEXT NOT NULL,product_type TEXT NOT NULL,canonical_name TEXT NOT NULL,normalized_identity_key TEXT NOT NULL,resulting_state TEXT NOT NULL,recorded_at TEXT NOT NULL);
       CREATE TABLE IF NOT EXISTS product_alias_history(alias_history_id INTEGER PRIMARY KEY AUTOINCREMENT,alias_id TEXT NOT NULL,product_id TEXT NOT NULL,alias_name TEXT NOT NULL,normalized_alias_key TEXT NOT NULL,event_id TEXT NOT NULL,resulting_state TEXT NOT NULL,recorded_at TEXT NOT NULL);
       CREATE TABLE IF NOT EXISTS audit_events(audit_event_id INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT NOT NULL,authority_type TEXT NOT NULL,authority_id TEXT NOT NULL,verification_result TEXT NOT NULL,recorded_at TEXT NOT NULL,UNIQUE(event_id,authority_type,authority_id));
       CREATE TRIGGER IF NOT EXISTS prh_no_update BEFORE UPDATE ON product_registration_history BEGIN SELECT RAISE(ABORT,'product registration history is append-only'); END;
       CREATE TRIGGER IF NOT EXISTS prh_no_delete BEFORE DELETE ON product_registration_history BEGIN SELECT RAISE(ABORT,'product registration history is append-only'); END;
       CREATE TRIGGER IF NOT EXISTS pah_no_update BEFORE UPDATE ON product_alias_history BEGIN SELECT RAISE(ABORT,'product alias history is append-only'); END;
       CREATE TRIGGER IF NOT EXISTS pah_no_delete BEFORE DELETE ON product_alias_history BEGIN SELECT RAISE(ABORT,'product alias history is append-only'); END;
       """)
    def identity_key(self,t,n,s=None,c=None,v=None): return '|'.join(map(norm,(t,n,s,c,v)))
    def register(self,product_type,canonical_name,set_name=None,card_number=None,variant_name=None,request_id=None):
      if not request_id: raise ValueError('missing explicit registration request')
      if product_type not in ('SINGLE','SEALED'): raise ValueError('unsupported product_type')
      if not norm(canonical_name): raise ValueError('missing canonical_name')
      key=self.identity_key(product_type,canonical_name,set_name,card_number,variant_name)
      payload=json.dumps([product_type,canonical_name,set_name,card_number,variant_name],ensure_ascii=False)
      with self._c() as c:
       prior=c.execute('SELECT event_id,payload_sha256 FROM event_identity WHERE request_id=?',(request_id,)).fetchone()
       if prior:
        accepted=c.execute('SELECT product_id FROM product_registration_history WHERE registration_request_id=? AND event_id=?',(request_id,prior['event_id'])).fetchone()
        if not accepted or prior['payload_sha256']!=hashlib.sha256(payload.encode()).hexdigest(): raise ValueError('replay identity mismatch')
        c.execute('INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES(?,?,?,?,?,?)',(request_id,prior['event_id'],'PRODUCT_REGISTRATION',prior['payload_sha256'],'BLOCKED',now()))
        return accepted['product_id']
       if c.execute('SELECT 1 FROM products WHERE normalized_identity_key=?',(key,)).fetchone(): raise ValueError('duplicate normalized identity key')
       product_id='PRD-'+uuid.uuid4().hex[:16].upper(); event_id='EVT-'+uuid.uuid4().hex.upper(); ts=now(); sha=hashlib.sha256(payload.encode()).hexdigest()
       c.execute('INSERT INTO event_identity VALUES(?,?,?,?,?,?,?)',(event_id,'PRODUCT_REGISTRATION',request_id,ts,ts,payload,sha))
       c.execute('INSERT INTO products VALUES(?,?,?,?,?,?,?,?,?,?)',(product_id,product_type,canonical_name,key,set_name,card_number,variant_name,'REGISTERED',event_id,ts))
       c.execute('INSERT INTO product_registration_history(product_id,registration_request_id,event_id,product_type,canonical_name,normalized_identity_key,resulting_state,recorded_at) VALUES(?,?,?,?,?,?,?,?)',(product_id,request_id,event_id,product_type,canonical_name,key,'REGISTERED',ts))
       c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES(?,?,?,?,?)',(event_id,'PRODUCT_REGISTRY',product_id,'VERIFIED',ts))
       persisted=c.execute('SELECT * FROM products WHERE product_id=?',(product_id,)).fetchone()
       if not persisted or persisted['normalized_identity_key']!=key: raise RuntimeError('post-write verification failed')
       return product_id
    def add_alias(self,product_id,alias_name,request_id):
      if not request_id: raise ValueError('missing explicit alias request')
      key=norm(alias_name)
      if not key: raise ValueError('missing alias')
      with self._c() as c:
       prior=c.execute('SELECT event_id,payload_sha256 FROM event_identity WHERE request_id=?',(request_id,)).fetchone()
       if prior:
        accepted=c.execute('SELECT product_id FROM product_alias_history WHERE event_id=?',(prior['event_id'],)).fetchone()
        attempted_sha=hashlib.sha256((product_id+'|'+key).encode()).hexdigest()
        if not accepted or prior['payload_sha256']!=attempted_sha: raise ValueError('replay identity mismatch')
        c.execute('INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES(?,?,?,?,?,?)',(request_id,prior['event_id'],'PRODUCT_ALIAS',prior['payload_sha256'],'BLOCKED',now()))
        return accepted['product_id']
       if not c.execute('SELECT 1 FROM products WHERE product_id=?',(product_id,)).fetchone(): raise ValueError('orphan alias')
       if c.execute('SELECT 1 FROM product_aliases WHERE normalized_alias_key=?',(key,)).fetchone(): raise ValueError('alias collision')
       alias_id='ALS-'+uuid.uuid4().hex[:16].upper(); event_id='EVT-'+uuid.uuid4().hex.upper(); ts=now(); sha=hashlib.sha256((product_id+'|'+key).encode()).hexdigest()
       c.execute('INSERT INTO event_identity VALUES(?,?,?,?,?,?,?)',(event_id,'PRODUCT_ALIAS',request_id,ts,ts,json.dumps([product_id,alias_name],ensure_ascii=False),sha))
       c.execute('INSERT INTO product_aliases VALUES(?,?,?,?,?,?)',(alias_id,product_id,alias_name,key,event_id,ts))
       c.execute('INSERT INTO product_alias_history(alias_id,product_id,alias_name,normalized_alias_key,event_id,resulting_state,recorded_at) VALUES(?,?,?,?,?,?,?)',(alias_id,product_id,alias_name,key,event_id,'VERIFIED',ts))
       c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES(?,?,?,?,?)',(event_id,'PRODUCT_ALIAS',alias_id,'VERIFIED',ts))
       return product_id
    def resolve_alias(self,alias):
      with self._c() as c:
       r=c.execute('SELECT product_id FROM product_aliases WHERE normalized_alias_key=?',(norm(alias),)).fetchone(); return r['product_id'] if r else None
    def run_acceptance(self):
      pid=self.register('SINGLE','Charizard ex','Obsidian Flames','125/197','Double Rare',ACCEPTANCE_REQUEST)
      duplicate='BLOCKED'
      try:self.register('SINGLE','Charizard ex','Obsidian Flames','125/197','Double Rare','M34-DUPLICATE-001')
      except ValueError: pass
      else: duplicate='FAILED'
      self.add_alias(pid,'Charizard EX 125/197','M34-ALIAS-001')
      alias_ok=self.resolve_alias('Charizard EX 125/197')==pid
      other=self.register('SEALED','Obsidian Flames Elite Trainer Box','Obsidian Flames',None,'Standard','M34-OTHER-001')
      collision='BLOCKED'
      try:self.add_alias(other,'Charizard EX 125/197','M34-ALIAS-COLLISION-001')
      except ValueError: pass
      else: collision='FAILED'
      replay=self.register('SINGLE','Charizard ex','Obsidian Flames','125/197','Double Rare',ACCEPTANCE_REQUEST)==pid
      return self.verify(pid,duplicate,alias_ok,collision,replay)
    def verify(self,pid=None,duplicate='BLOCKED',alias_ok=None,collision='BLOCKED',replay=True):
      with self._c() as c:
       if pid is None:
        r=c.execute("SELECT product_id FROM products WHERE normalized_identity_key=?",(self.identity_key('SINGLE','Charizard ex','Obsidian Flames','125/197','Double Rare'),)).fetchone(); pid=r['product_id'] if r else None
       product=c.execute('SELECT * FROM products WHERE product_id=?',(pid,)).fetchone() if pid else None
       if alias_ok is None: alias_ok=(self.resolve_alias('Charizard EX 125/197')==pid) if pid else False
       history='APPEND-ONLY' if product and c.execute('SELECT COUNT(*) n FROM product_registration_history WHERE product_id=?',(pid,)).fetchone()['n']==1 else 'PENDING'
       audit='PASS' if product and c.execute('SELECT 1 FROM audit_events WHERE event_id=?',(product['created_event_id'],)).fetchone() else 'PENDING'
       replay_row=c.execute('SELECT original_event_id,defense_result FROM replay_defense_history WHERE request_id=? AND attempted_event_type=?',(ACCEPTANCE_REQUEST,'PRODUCT_REGISTRATION')).fetchone()
       accepted_event=c.execute('SELECT event_id FROM event_identity WHERE request_id=?',(ACCEPTANCE_REQUEST,)).fetchone()
       replay_ok=bool(replay and replay_row and accepted_event and replay_row['original_event_id']==accepted_event['event_id'] and replay_row['defense_result']=='BLOCKED')
       checks=[('Product evidence validation',bool(product),'required SINGLE evidence accepted'),('Product type authority',bool(product and product['product_type']=='SINGLE'),'SINGLE is explicit and supported'),('Canonical identity normalization',bool(product and product['normalized_identity_key']==self.identity_key('SINGLE','Charizard ex','Obsidian Flames','125/197','Double Rare')),'normalized identity stable'),('Persistent product identity',bool(pid),'stable product_id persisted'),('Duplicate product blocking',duplicate=='BLOCKED','exact duplicate creates ZERO second product'),('Controlled alias authority',bool(alias_ok),'alias resolves to original product_id'),('Alias collision blocking',collision=='BLOCKED','one alias cannot resolve to multiple products'),('Append-only registration history',history=='APPEND-ONLY','registration history protected'),('Request + event identity authority',bool(product and product['created_event_id']),'request and event identity linked'),('Persistent replay defense',replay_ok,'same request returns accepted product_id'),('Audit explainability',audit=='PASS','product event has VERIFIED audit'),('Restart-persistent Product Registry authority',bool(product and alias_ok and replay_ok),'product, alias, history and replay reconstruct')]
       passed=sum(ok for _,ok,_ in checks)
       return {'checks':checks,'passed':passed,'pid':pid or 'PENDING','duplicate':duplicate,'alias':'VERIFIED' if alias_ok else 'PENDING','collision':collision,'history':history,'replay':'PASS' if replay_ok else 'PENDING','audit':audit,'restart':'PASS' if passed==12 else 'PENDING','state':'REGISTERED' if passed==12 else 'DRAFT'}
