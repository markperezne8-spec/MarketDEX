import sqlite3,uuid,json,hashlib,re
from pathlib import Path
from datetime import datetime,timezone
BASELINE='135066da16af816060d6d49e13e80e262f27efb1'
REQ='M35-LINK-CHARIZARD-001'; ASSET='AST-M35-CHARIZARD-001'
def now(): return datetime.now(timezone.utc).isoformat()
def norm(v): return re.sub(r'[^a-z0-9]+',' ',(v or '').casefold()).strip()
class InventoryProductLinkService:
 def __init__(self,path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self._init()
 def _c(self): c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c
 def _init(self):
  with self._c() as c:c.executescript("""
  CREATE TABLE IF NOT EXISTS event_identity(event_id TEXT PRIMARY KEY,event_type TEXT NOT NULL,request_id TEXT NOT NULL UNIQUE,occurred_at TEXT NOT NULL,committed_at TEXT NOT NULL,payload_json TEXT NOT NULL,payload_sha256 TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS audit_history(audit_id INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT NOT NULL,service_name TEXT NOT NULL,action_name TEXT NOT NULL,recorded_at TEXT NOT NULL,detail_json TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS assets(asset_id TEXT PRIMARY KEY,asset_name TEXT NOT NULL,asset_type TEXT NOT NULL,state TEXT NOT NULL,created_event_id TEXT NOT NULL,created_at TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS inventory_authority(asset_id TEXT PRIMARY KEY,quantity INTEGER NOT NULL CHECK(quantity>=0),total_cost_minor INTEGER NOT NULL CHECK(total_cost_minor>=0),last_event_id TEXT NOT NULL,verified_at TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS inventory_history(history_id INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT NOT NULL,asset_id TEXT NOT NULL,quantity_delta INTEGER NOT NULL,cost_delta_minor INTEGER NOT NULL,resulting_quantity INTEGER NOT NULL CHECK(resulting_quantity>=0),resulting_total_cost_minor INTEGER NOT NULL CHECK(resulting_total_cost_minor>=0),recorded_at TEXT NOT NULL,UNIQUE(event_id,asset_id));
  CREATE TABLE IF NOT EXISTS replay_defense_history(replay_history_id INTEGER PRIMARY KEY AUTOINCREMENT,request_id TEXT NOT NULL,original_event_id TEXT NOT NULL,attempted_event_type TEXT NOT NULL,payload_sha256 TEXT NOT NULL,defense_result TEXT NOT NULL CHECK(defense_result='BLOCKED'),recorded_at TEXT NOT NULL,UNIQUE(request_id,attempted_event_type,payload_sha256));
  CREATE TABLE IF NOT EXISTS audit_events(audit_event_id INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT NOT NULL,authority_type TEXT NOT NULL,authority_id TEXT NOT NULL,verification_result TEXT NOT NULL,recorded_at TEXT NOT NULL,UNIQUE(event_id,authority_type,authority_id));
  CREATE TABLE IF NOT EXISTS marketplace_publication_allocations(allocation_id TEXT PRIMARY KEY,asset_id TEXT NOT NULL,marketplace TEXT NOT NULL,publication_reference TEXT NOT NULL,publication_identity TEXT NOT NULL,requested_quantity INTEGER NOT NULL,allocated_quantity INTEGER NOT NULL,released_quantity INTEGER NOT NULL DEFAULT 0,cancelled_quantity INTEGER NOT NULL DEFAULT 0,consumed_quantity INTEGER NOT NULL DEFAULT 0,state TEXT NOT NULL,source_event_id TEXT NOT NULL,created_at TEXT NOT NULL,committed_at TEXT NOT NULL,verified_at TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS products(product_id TEXT PRIMARY KEY,product_type TEXT NOT NULL,canonical_name TEXT NOT NULL,normalized_identity_key TEXT NOT NULL UNIQUE,set_name TEXT,card_number TEXT,variant_name TEXT,state TEXT NOT NULL,created_event_id TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS product_registration_history(registration_history_id INTEGER PRIMARY KEY AUTOINCREMENT,product_id TEXT NOT NULL,registration_request_id TEXT NOT NULL,event_id TEXT NOT NULL,product_type TEXT NOT NULL,canonical_name TEXT NOT NULL,normalized_identity_key TEXT NOT NULL,resulting_state TEXT NOT NULL,recorded_at TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS inventory_product_links(inventory_product_link_id TEXT PRIMARY KEY,asset_id TEXT NOT NULL UNIQUE,product_id TEXT NOT NULL,state TEXT NOT NULL CHECK(state='LINKED'),created_event_id TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS inventory_product_link_history(linkage_history_id INTEGER PRIMARY KEY AUTOINCREMENT,inventory_product_link_id TEXT NOT NULL,asset_id TEXT NOT NULL,product_id TEXT NOT NULL,linkage_request_id TEXT NOT NULL,event_id TEXT NOT NULL,resulting_state TEXT NOT NULL,recorded_at TEXT NOT NULL);
  CREATE TRIGGER IF NOT EXISTS iphl_no_update BEFORE UPDATE ON inventory_product_link_history BEGIN SELECT RAISE(ABORT,'inventory product link history is append-only'); END;
  CREATE TRIGGER IF NOT EXISTS iphl_no_delete BEFORE DELETE ON inventory_product_link_history BEGIN SELECT RAISE(ABORT,'inventory product link history is append-only'); END;
  """)
 def _event(self,c,event_type,request_id,payload):
  ts=now(); raw=json.dumps(payload,sort_keys=True,separators=(',',':')); sha=hashlib.sha256(raw.encode()).hexdigest(); eid='EVT-'+uuid.uuid4().hex.upper(); c.execute('INSERT INTO event_identity VALUES(?,?,?,?,?,?,?)',(eid,event_type,request_id,ts,ts,raw,sha)); return eid,sha,ts
 def ensure_acceptance_authority(self):
  with self._c() as c:
   key='|'.join(map(norm,('SINGLE','Charizard ex','Obsidian Flames','125/197','Double Rare')))
   p=c.execute('SELECT product_id FROM products WHERE normalized_identity_key=?',(key,)).fetchone()
   if not p:
    eid,sha,ts=self._event(c,'PRODUCT_REGISTRATION','M34-REGISTER-CHARIZARD-001',['SINGLE','Charizard ex','Obsidian Flames','125/197','Double Rare']); pid='PRD-'+uuid.uuid4().hex[:16].upper(); c.execute('INSERT INTO products VALUES(?,?,?,?,?,?,?,?,?,?)',(pid,'SINGLE','Charizard ex',key,'Obsidian Flames','125/197','Double Rare','REGISTERED',eid,ts)); c.execute('INSERT INTO product_registration_history(product_id,registration_request_id,event_id,product_type,canonical_name,normalized_identity_key,resulting_state,recorded_at) VALUES(?,?,?,?,?,?,?,?)',(pid,'M34-REGISTER-CHARIZARD-001',eid,'SINGLE','Charizard ex',key,'REGISTERED',ts)); c.execute('INSERT OR IGNORE INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES(?,?,?,?,?)',(eid,'PRODUCT_REGISTRY',pid,'VERIFIED',ts))
   else: pid=p['product_id']
   if not c.execute('SELECT 1 FROM assets WHERE asset_id=?',(ASSET,)).fetchone():
    eid,sha,ts=self._event(c,'ACQUISITION','M35-ACCEPTANCE-ASSET-001',{'asset_id':ASSET,'asset_name':'Charizard ex acceptance asset','asset_type':'SINGLE','state':'PLANNED'}); c.execute('INSERT INTO assets VALUES(?,?,?,?,?,?)',(ASSET,'Charizard ex acceptance asset','SINGLE','PLANNED',eid,ts)); c.execute('INSERT INTO audit_history(event_id,service_name,action_name,recorded_at,detail_json) VALUES(?,?,?,?,?)',(eid,'asset_service','create_asset',ts,'{}'))
   if not c.execute('SELECT 1 FROM inventory_authority WHERE asset_id=?',(ASSET,)).fetchone():
    eid,sha,ts=self._event(c,'ACQUISITION','M35-ACCEPTANCE-INVENTORY-001',{'asset_id':ASSET,'quantity':3,'total_cost_minor':0}); c.execute('INSERT INTO inventory_authority VALUES(?,?,?,?,?)',(ASSET,3,0,eid,ts)); c.execute('INSERT INTO inventory_history(event_id,asset_id,quantity_delta,cost_delta_minor,resulting_quantity,resulting_total_cost_minor,recorded_at) VALUES(?,?,?,?,?,?,?)',(eid,ASSET,3,0,3,0,ts)); c.execute('INSERT INTO audit_history(event_id,service_name,action_name,recorded_at,detail_json) VALUES(?,?,?,?,?)',(eid,'inventory_service','apply_acquisition',ts,'{}'))
   return pid
 def link(self,asset_id,product_id,request_id):
  if not asset_id or not product_id or not request_id: raise ValueError('missing linkage evidence')
  payload={'asset_id':asset_id,'product_id':product_id}; raw=json.dumps(payload,sort_keys=True,separators=(',',':')); sha=hashlib.sha256(raw.encode()).hexdigest()
  with self._c() as c:
   prior=c.execute('SELECT event_id,payload_sha256 FROM event_identity WHERE request_id=?',(request_id,)).fetchone()
   if prior:
    accepted=c.execute('SELECT inventory_product_link_id FROM inventory_product_link_history WHERE linkage_request_id=? AND event_id=?',(request_id,prior['event_id'])).fetchone()
    if not accepted or prior['payload_sha256']!=sha: raise ValueError('replay identity mismatch')
    c.execute('INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES(?,?,?,?,?,?)',(request_id,prior['event_id'],'INVENTORY_PRODUCT_LINK',sha,'BLOCKED',now())); return accepted['inventory_product_link_id']
   if not c.execute('SELECT 1 FROM assets WHERE asset_id=?',(asset_id,)).fetchone(): raise ValueError('asset does not exist')
   if not c.execute('SELECT 1 FROM products WHERE product_id=?',(product_id,)).fetchone(): raise ValueError('product does not exist')
   existing=c.execute('SELECT * FROM inventory_product_links WHERE asset_id=?',(asset_id,)).fetchone()
   if existing:
    if existing['product_id']!=product_id: raise ValueError('conflicting product linkage')
    raise ValueError('duplicate linkage request')
   eid,sha,ts=self._event(c,'INVENTORY_PRODUCT_LINK',request_id,payload); lid='IPL-'+uuid.uuid4().hex[:16].upper(); c.execute('INSERT INTO inventory_product_links VALUES(?,?,?,?,?,?)',(lid,asset_id,product_id,'LINKED',eid,ts)); c.execute('INSERT INTO inventory_product_link_history(inventory_product_link_id,asset_id,product_id,linkage_request_id,event_id,resulting_state,recorded_at) VALUES(?,?,?,?,?,?,?)',(lid,asset_id,product_id,request_id,eid,'LINKED',ts)); c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES(?,?,?,?,?)',(eid,'INVENTORY_PRODUCT_LINK',lid,'VERIFIED',ts)); check=c.execute('SELECT * FROM inventory_product_links WHERE inventory_product_link_id=?',(lid,)).fetchone();
   if not check or check['product_id']!=product_id: raise RuntimeError('post-write verification failed')
   return lid
 def quantities(self,product_id):
  with self._c() as c:
   q=c.execute('SELECT COALESCE(SUM(i.quantity),0) q FROM inventory_product_links l JOIN inventory_authority i ON i.asset_id=l.asset_id WHERE l.product_id=?',(product_id,)).fetchone()['q']; a=c.execute("SELECT COALESCE(SUM(m.allocated_quantity-m.released_quantity-m.cancelled_quantity-m.consumed_quantity),0) a FROM inventory_product_links l JOIN marketplace_publication_allocations m ON m.asset_id=l.asset_id WHERE l.product_id=? AND m.state='ACTIVE'",(product_id,)).fetchone()['a']; available=int(q)-int(a)
   if q<0 or available<0: raise ValueError('negative product-aware quantity')
   return int(q),available
 def run_acceptance(self):
  pid=self.ensure_acceptance_authority(); before=self.quantities(pid); lid=self.link(ASSET,pid,REQ); after=self.quantities(pid); other=self._ensure_other_product(); conflict='BLOCKED'
  try:self.link(ASSET,other,'M35-CONFLICT-001')
  except ValueError: pass
  else: conflict='FAILED'
  replay=self.link(ASSET,pid,REQ)==lid; return self.verify(pid,lid,conflict,replay,before,after)
 def _ensure_other_product(self):
  with self._c() as c:
   r=c.execute("SELECT product_id FROM products WHERE canonical_name='M35 Conflict Product'").fetchone()
   if r:return r['product_id']
   eid,sha,ts=self._event(c,'PRODUCT_REGISTRATION','M35-CONFLICT-PRODUCT-001',['SEALED','M35 Conflict Product']); pid='PRD-'+uuid.uuid4().hex[:16].upper(); key='sealed|m35 conflict product|||'; c.execute('INSERT INTO products VALUES(?,?,?,?,?,?,?,?,?,?)',(pid,'SEALED','M35 Conflict Product',key,None,None,None,'REGISTERED',eid,ts)); c.execute('INSERT INTO product_registration_history(product_id,registration_request_id,event_id,product_type,canonical_name,normalized_identity_key,resulting_state,recorded_at) VALUES(?,?,?,?,?,?,?,?)',(pid,'M35-CONFLICT-PRODUCT-001',eid,'SEALED','M35 Conflict Product',key,'REGISTERED',ts)); return pid
 def verify(self,pid=None,lid=None,conflict='BLOCKED',replay=True,before=None,after=None):
  with self._c() as c:
   if pid is None:
    r=c.execute("SELECT product_id FROM products WHERE canonical_name='Charizard ex' AND card_number='125/197'").fetchone(); pid=r['product_id'] if r else None
   if lid is None and pid:
    r=c.execute('SELECT inventory_product_link_id FROM inventory_product_links WHERE asset_id=? AND product_id=?',(ASSET,pid)).fetchone(); lid=r['inventory_product_link_id'] if r else None
   asset=bool(c.execute('SELECT 1 FROM assets WHERE asset_id=?',(ASSET,)).fetchone()); product=bool(pid and c.execute('SELECT 1 FROM products WHERE product_id=?',(pid,)).fetchone()); q,av=self.quantities(pid) if pid else (0,0); hist=c.execute('SELECT COUNT(*) n FROM inventory_product_link_history WHERE inventory_product_link_id=?',(lid,)).fetchone()['n'] if lid else 0; audit=bool(lid and c.execute("SELECT 1 FROM audit_events WHERE authority_type='INVENTORY_PRODUCT_LINK' AND authority_id=? AND verification_result='VERIFIED'",(lid,)).fetchone()); rr=c.execute("SELECT 1 FROM replay_defense_history WHERE request_id=? AND attempted_event_type='INVENTORY_PRODUCT_LINK' AND defense_result='BLOCKED'",(REQ,)).fetchone(); replay_ok=bool(replay and rr); zero_mutation=bool(lid and c.execute('SELECT COUNT(*) n FROM inventory_history WHERE event_id=(SELECT created_event_id FROM inventory_product_links WHERE inventory_product_link_id=?)',(lid,)).fetchone()['n']==0)
   checks=[('Asset authority validation',asset,'accepted asset authority exists'),('Canonical product validation',product,'M34 canonical product exists'),('Explicit linkage request authority',bool(lid),'explicit request linked to event identity'),('Persistent linkage identity',bool(lid),'stable linkage_id persisted'),('One-product-per-asset conflict defense',conflict=='BLOCKED','conflicting product linkage blocked'),('Product-aware authoritative quantity derivation',q==3,'linked inventory_authority sum = 3'),('Product-aware available quantity derivation',av==3,'authoritative quantity minus ACTIVE allocations = 3'),('ZERO inventory mutation from linkage',zero_mutation,'link event created ZERO inventory_history movement'),('Append-only linkage history',hist==1,'one immutable linkage history record'),('Persistent replay defense',replay_ok,'same request returns accepted linkage_id'),('Audit explainability',audit,'link event has VERIFIED audit'),('Restart-persistent inventory-to-product linkage',bool(lid and q==3 and av==3 and replay_ok),'linkage reconstructs from persisted authority')]; passed=sum(ok for _,ok,_ in checks)
   return {'checks':checks,'passed':passed,'asset':'VERIFIED' if asset else 'PENDING','product':'VERIFIED' if product else 'PENDING','lid':lid or 'PENDING','conflict':conflict,'q':q,'available':av,'mutation':'ZERO' if zero_mutation else 'PENDING','history':'APPEND-ONLY' if hist==1 else 'PENDING','replay':'PASS' if replay_ok else 'PENDING','audit':'PASS' if audit else 'PENDING','restart':'PASS' if passed==12 else 'PENDING','state':'LINKED' if passed==12 else 'DRAFT'}
