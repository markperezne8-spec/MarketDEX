from uuid import uuid4
from uuid import uuid4
from datetime import datetime,timezone
from .base_service import AuthoritativeService
from core.event_repository import ReplayRejected
def now(): return datetime.now(timezone.utc).isoformat()
class AuthorityBlocked(ValueError): pass

class MarketplaceLifecycleService(AuthoritativeService):
 service_name='marketplace_lifecycle_service'
 def __init__(self,database,events): super().__init__(database,events); self.db=database
 def event(self,c,event_type,request_id,payload):
  event=self._new_event(event_type,request_id,payload); self._append_event_and_audit(c,event,event_type.lower()); return event.event_id,event.committed_at
 def reject_replay(self,c,event_type,request_id,payload):
  event=self._new_event(event_type,request_id,payload); existing=c.execute('SELECT event_id FROM event_identity WHERE request_id=?',(request_id,)).fetchone()
  if existing is not None:
   c.execute('INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES (?,?,?,?,?,?)',(request_id,existing['event_id'],event_type,event.payload_sha256,'BLOCKED',event.committed_at)); raise ReplayRejected('Request already committed — ZERO second authoritative mutation')
 def audit(self,c,eid,typ,aid,ts): c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(eid,typ,aid,'VERIFIED',ts))


 def available_quantity(self,asset_id,c=None):
  own=c is None; c=c or self.db.connect()
  try:
   inv=c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=?',(asset_id,)).fetchone(); qty=int(inv['quantity']) if inv else 0
   active=int(c.execute("SELECT COALESCE(SUM(allocated_quantity-released_quantity-cancelled_quantity-consumed_quantity),0) n FROM marketplace_publication_allocations WHERE asset_id=? AND state='ACTIVE'",(asset_id,)).fetchone()['n'])
   return qty-active
  finally:
   if own:c.close()
 def active_allocation_quantity(self,asset_id,c=None):
  own=c is None; c=c or self.db.connect()
  try:return int(c.execute("SELECT COALESCE(SUM(allocated_quantity-released_quantity-cancelled_quantity-consumed_quantity),0) n FROM marketplace_publication_allocations WHERE asset_id=? AND state='ACTIVE'",(asset_id,)).fetchone()['n'])
  finally:
   if own:c.close()
 def publication_eligibility(self,**k):
  try:q=int(k.get('requested_allocation_quantity',0))
  except:q=0
  aid=str(k.get('asset_id','')).strip(); evidence=bool(k.get('evidence_complete')) and bool(str(k.get('evidence_type','')).strip()) and bool(str(k.get('evidence_reference','')).strip())
  explicit=str(k.get('intent','')).strip().upper()=='LISTED' and bool(str(k.get('request_id','')).strip())
  identity=bool(str(k.get('marketplace','')).strip()) and bool(str(k.get('publication_reference','')).strip()) and bool(str(k.get('publication_identity','')).strip())
  with self.db.connect() as c: inv=c.execute('SELECT 1 FROM inventory_authority WHERE asset_id=?',(aid,)).fetchone(); av=self.available_quantity(aid,c) if inv else 0
  ok=bool(inv) and evidence and explicit and identity and q>0 and q<=av
  return {'publication_eligible':ok,'control_result':'CONTROLLED' if ok else 'BLOCKED','available_quantity':av}
 def list_publication(self,*,request_id,allocation_id,asset_id,marketplace,requested_allocation_quantity,publication_reference,publication_identity,evidence_type,evidence_reference,evidence_complete,intent):
  gate=self.publication_eligibility(**{k:v for k,v in locals().items() if k!='self'})
  if not gate['publication_eligible']: raise AuthorityBlocked('Publication authority BLOCKED')
  q=int(requested_allocation_quantity); payload={k:v for k,v in locals().items() if k not in ('self','gate')}
  with self.db.transaction() as c:
   av=self.available_quantity(asset_id,c)
   if q<=0 or q>av: raise AuthorityBlocked('Stale availability or cross-channel capacity BLOCKED')
   if c.execute('SELECT 1 FROM marketplace_publication_allocations WHERE allocation_id=?',(allocation_id,)).fetchone(): raise AuthorityBlocked('Duplicate allocation execution')
   eid,ts=self.event(c,'LISTED',request_id,payload); lifecycle=f'LIFE-{uuid4()}'
   c.execute('INSERT INTO marketplace_publication_allocations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(allocation_id,asset_id,marketplace,publication_reference,publication_identity,q,q,0,0,0,'ACTIVE',eid,ts,ts,ts))
   c.execute('INSERT INTO publication_lifecycle_events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(lifecycle,allocation_id,'LISTED',q,evidence_type,evidence_reference,1,marketplace,publication_reference,publication_identity,None,None,None,eid,request_id,f'LISTED:{request_id}',ts,ts,ts))
   self.audit(c,eid,'LISTED',allocation_id,ts); self._reconcile(c,asset_id,eid)
  return eid
 def release(self,*,request_id,allocation_id,release_quantity,evidence_type,evidence_reference,evidence_complete,intent):
  try:q=int(release_quantity)
  except:q=0
  if str(intent).upper()!='RELEASE' or not evidence_complete or not str(evidence_type).strip() or not str(evidence_reference).strip() or q<=0: raise AuthorityBlocked('Release authority BLOCKED')
  payload={k:v for k,v in locals().items() if k!='self'}
  with self.db.transaction() as c:
   self.reject_replay(c,'RELEASE',request_id,payload)
   a=c.execute('SELECT * FROM marketplace_publication_allocations WHERE allocation_id=?',(allocation_id,)).fetchone()
   if a is None or a['state']!='ACTIVE': raise AuthorityBlocked('Active allocation required')
   remaining=int(a['allocated_quantity'])-int(a['released_quantity'])-int(a['cancelled_quantity'])-int(a['consumed_quantity'])
   if q>remaining: raise AuthorityBlocked('Release exceeds active allocation')
   eid,ts=self.event(c,'RELEASE',request_id,payload); lifecycle=f'LIFE-{uuid4()}'
   newrel=int(a['released_quantity'])+q; newstate='RELEASED' if q==remaining else 'ACTIVE'
   c.execute('UPDATE marketplace_publication_allocations SET released_quantity=?,state=?,verified_at=? WHERE allocation_id=?',(newrel,newstate,ts,allocation_id))
   c.execute('INSERT INTO publication_lifecycle_events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(lifecycle,allocation_id,'RELEASE',q,evidence_type,evidence_reference,1,a['marketplace'],a['publication_reference'],a['publication_identity'],None,None,a['source_event_id'],eid,request_id,f'RELEASE:{request_id}',ts,ts,ts))
   self.audit(c,eid,'RELEASE',allocation_id,ts); self._reconcile(c,a['asset_id'],eid)
  return eid
 def cancel(self,*,request_id,allocation_id,evidence_type,evidence_reference,evidence_complete,intent):
  if str(intent).upper()!='CANCELLATION' or not evidence_complete or not str(evidence_type).strip() or not str(evidence_reference).strip(): raise AuthorityBlocked('Cancellation authority BLOCKED')
  payload={k:v for k,v in locals().items() if k!='self'}
  with self.db.transaction() as c:
   self.reject_replay(c,'CANCELLATION',request_id,payload)
   a=c.execute('SELECT * FROM marketplace_publication_allocations WHERE allocation_id=?',(allocation_id,)).fetchone()
   if a is None or a['state']!='ACTIVE': raise AuthorityBlocked('Active allocation required')
   remaining=int(a['allocated_quantity'])-int(a['released_quantity'])-int(a['cancelled_quantity'])-int(a['consumed_quantity'])
   eid,ts=self.event(c,'CANCELLATION',request_id,payload); lifecycle=f'LIFE-{uuid4()}'
   c.execute("UPDATE marketplace_publication_allocations SET cancelled_quantity=?,state='CANCELLED',verified_at=? WHERE allocation_id=?",(int(a['cancelled_quantity'])+remaining,ts,allocation_id))
   c.execute('INSERT INTO publication_lifecycle_events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(lifecycle,allocation_id,'CANCELLATION',remaining,evidence_type,evidence_reference,1,a['marketplace'],a['publication_reference'],a['publication_identity'],None,None,a['source_event_id'],eid,request_id,f'CANCELLATION:{request_id}',ts,ts,ts))
   self.audit(c,eid,'CANCELLATION',allocation_id,ts); self._reconcile(c,a['asset_id'],eid)
  return eid
 def sold_conversion(self,*,request_id,allocation_id,sale_id,sale_event_id,marketplace,sale_quantity,intent='SOLD_CONVERSION'):
  q=int(sale_quantity)
  if str(intent).upper()!='SOLD_CONVERSION': raise AuthorityBlocked('Explicit SOLD conversion request required')
  payload={k:v for k,v in locals().items() if k!='self'}
  with self.db.transaction() as c:
   self.reject_replay(c,'SOLD_CONVERSION',request_id,payload)
   a=c.execute('SELECT * FROM marketplace_publication_allocations WHERE allocation_id=?',(allocation_id,)).fetchone(); sale=c.execute('SELECT * FROM sales WHERE sale_id=? AND created_event_id=?',(sale_id,sale_event_id)).fetchone()
   if a is None or a['state']!='ACTIVE': raise AuthorityBlocked('Active allocation required')
   if sale is None: raise AuthorityBlocked('Authoritative M24 sale required')
   if sale['asset_id']!=a['asset_id'] or marketplace!=a['marketplace']: raise AuthorityBlocked('Sale marketplace or allocation relationship mismatch')
   remaining=int(a['allocated_quantity'])-int(a['released_quantity'])-int(a['cancelled_quantity'])-int(a['consumed_quantity'])
   if q<=0 or q!=int(sale['quantity']) or q>remaining: raise AuthorityBlocked('Sale quantity mismatch')
   inv_before=int(c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=?',(a['asset_id'],)).fetchone()['quantity']); fin_before=int(c.execute('SELECT COUNT(*) FROM sales_financial_history WHERE sale_id=?',(sale_id,)).fetchone()[0])
   eid,ts=self.event(c,'SOLD_CONVERSION',request_id,payload); lifecycle=f'LIFE-{uuid4()}'
   consumed=int(a['consumed_quantity'])+q; state='CONSUMED' if q==remaining else 'ACTIVE'
   c.execute('UPDATE marketplace_publication_allocations SET consumed_quantity=?,state=?,verified_at=? WHERE allocation_id=?',(consumed,state,ts,allocation_id))
   c.execute('INSERT INTO publication_lifecycle_events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(lifecycle,allocation_id,'SOLD_CONVERSION',q,'M24_SALE',sale_id,1,a['marketplace'],a['publication_reference'],a['publication_identity'],sale_id,sale_event_id,a['source_event_id'],eid,request_id,f'SOLD_CONVERSION:{request_id}',ts,ts,ts))
   if int(c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=?',(a['asset_id'],)).fetchone()['quantity'])!=inv_before: raise RuntimeError('M30 created second inventory decrement')
   if int(c.execute('SELECT COUNT(*) FROM sales_financial_history WHERE sale_id=?',(sale_id,)).fetchone()[0])!=fin_before: raise RuntimeError('M30 created second financial event')
   self.audit(c,eid,'SOLD_CONVERSION',allocation_id,ts); self._reconcile(c,a['asset_id'],eid)
  return eid
 def _reconcile(self,c,asset_id,source_event_id):
  active=self.active_allocation_quantity(asset_id,c); inv=c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=?',(asset_id,)).fetchone(); qty=int(inv['quantity']) if inv else 0; av=qty-active
  if active<0 or av<0:
   ex=f'EX-{uuid4()}'; ts=now(); c.execute('INSERT INTO exception_authority(exception_id,source_event_id,exception_type,evidence,state,event_id,created_at) VALUES (?,?,?,?,?,?,?)',(ex,source_event_id,'ALLOCATION_VARIANCE',f'asset={asset_id}; quantity={qty}; active={active}; available={av}','REVIEW',source_event_id,ts)); raise AuthorityBlocked('Allocation variance FAIL CLOSED')
  return active,av
