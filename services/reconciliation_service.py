from datetime import datetime,timezone
from uuid import uuid4
from core.event_repository import ReplayRejected
from .base_service import AuthoritativeService

def now(): return datetime.now(timezone.utc).isoformat()
class ReconciliationBlocked(ValueError): pass

class ReconciliationService(AuthoritativeService):
 service_name='reconciliation_service'
 def __init__(self,database,events,inventory_service,repo,lifecycle):
  super().__init__(database,events); self.inventory_service=inventory_service; self.repo=repo; self.lifecycle=lifecycle
 def remaining_quantity_truth(self,c,asset_id):
  orphan=int(c.execute('SELECT COUNT(*) FROM inventory_history h LEFT JOIN event_identity e ON e.event_id=h.event_id WHERE h.asset_id=? AND e.event_id IS NULL',(asset_id,)).fetchone()[0])
  if orphan: raise ReconciliationBlocked('Orphan inventory movement BLOCKED')
  return int(c.execute('SELECT COALESCE(SUM(quantity_delta),0) FROM inventory_history WHERE asset_id=?',(asset_id,)).fetchone()[0])
 def evaluate(self,*,asset_id,evidence_type,evidence_reference,evidence_complete,observed_quantity,reconciliation_reason,request_id,explicit_intent):
  try: observed=int(observed_quantity)
  except: return {'eligible':False,'control_result':'BLOCKED'}
  if isinstance(observed_quantity,float) and not observed_quantity.is_integer(): return {'eligible':False,'control_result':'BLOCKED'}
  with self.database.connect() as c:
   asset=c.execute('SELECT 1 FROM assets WHERE asset_id=?',(asset_id,)).fetchone(); inv=c.execute('SELECT * FROM inventory_authority WHERE asset_id=?',(asset_id,)).fetchone()
   if not asset or not inv: return {'eligible':False,'control_result':'BLOCKED'}
   remaining=self.remaining_quantity_truth(c,asset_id); current=int(inv['quantity']); variance=observed-current; authority_variance=remaining-current
   active=self.lifecycle.active_allocation_quantity(asset_id,c); available=current-active
  evidence=bool(evidence_complete and str(evidence_type).strip() and str(evidence_reference).strip())
  explicit=str(explicit_intent).upper()=='RECONCILE' and bool(str(request_id).strip()) and bool(str(reconciliation_reason).strip())
  explainable=authority_variance==0
  eligible=bool(observed>=0 and evidence and explicit and variance!=0 and explainable and current+variance>=0)
  return {'eligible':eligible,'control_result':'CONTROLLED' if eligible else 'BLOCKED','remaining':remaining,'current':current,'observed':observed,'variance':variance,'authorized_delta':variance if eligible else None,'active':active,'available':available,'authority_variance':authority_variance}
 def reconcile(self,*,reconciliation_id,asset_id,evidence_type,evidence_reference,evidence_complete,observed_quantity,reconciliation_reason,request_id,explicit_intent):
  payload={'reconciliation_id':reconciliation_id,'asset_id':asset_id,'evidence_type':evidence_type,'evidence_reference':evidence_reference,'evidence_complete':bool(evidence_complete),'observed_quantity':observed_quantity,'reconciliation_reason':reconciliation_reason,'explicit_intent':explicit_intent}
  event=self._new_event('INVENTORY_RECONCILIATION',request_id,payload)
  with self.database.transaction() as c:
   existing=c.execute('SELECT event_id FROM event_identity WHERE request_id=?',(request_id,)).fetchone()
   if existing:
    c.execute('INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES (?,?,?,?,?,?)',(request_id,existing['event_id'],event.event_type,event.payload_sha256,'BLOCKED',event.committed_at)); raise ReplayRejected('Committed reconciliation replay BLOCKED — ZERO second authoritative mutation')
   gate=self.evaluate(asset_id=asset_id,evidence_type=evidence_type,evidence_reference=evidence_reference,evidence_complete=evidence_complete,observed_quantity=observed_quantity,reconciliation_reason=reconciliation_reason,request_id=request_id,explicit_intent=explicit_intent)
   if not gate.get('eligible'): raise ReconciliationBlocked('Reconciliation authority BLOCKED')
   # Immediate final revalidation inside write transaction.
   inv=c.execute('SELECT * FROM inventory_authority WHERE asset_id=?',(asset_id,)).fetchone(); current=int(inv['quantity']); remaining=self.remaining_quantity_truth(c,asset_id); observed=int(observed_quantity); delta=observed-current
   if current!=gate['current'] or remaining!=gate['remaining'] or delta!=gate['authorized_delta'] or current+delta<0: raise ReconciliationBlocked('Stale reconciliation authority BLOCKED')
   if int(inv['total_cost_minor'])!=0: raise ReconciliationBlocked('Cost treatment ambiguity BLOCKED')
   ts=event.committed_at
   self._append_event_and_audit(c,event,'reconcile')
   rr=self.repo
   rr.append_state(c,reconciliation_id=reconciliation_id,asset_id=asset_id,state='ELIGIBLE',event_id=event.event_id,request_id=request_id,evidence_reference=evidence_reference,remaining=remaining,current=current,observed=observed,variance=delta,authorized_delta=delta,control_result='CONTROLLED',recorded_at=ts)
   rr.append_state(c,reconciliation_id=reconciliation_id,asset_id=asset_id,state='COMMITTED',event_id=event.event_id,request_id=request_id,evidence_reference=evidence_reference,remaining=remaining,current=current,observed=observed,variance=delta,authorized_delta=delta,control_result='CONTROLLED',recorded_at=ts)
   nq,_=self.inventory_service.apply_reconciliation_delta(c,asset_id=asset_id,authorized_delta=delta,event_id=event.event_id,recorded_at=ts)
   if nq!=observed: raise RuntimeError('Post-write verification mismatch')
   hist=c.execute('SELECT history_id FROM inventory_history WHERE event_id=? AND asset_id=?',(event.event_id,asset_id)).fetchone(); ledger=self.remaining_quantity_truth(c,asset_id)
   if ledger!=nq: raise RuntimeError('Inventory ledger mismatch')
   rr.append_state(c,reconciliation_id=reconciliation_id,asset_id=asset_id,state='VERIFIED',event_id=event.event_id,request_id=request_id,evidence_reference=evidence_reference,remaining=remaining,current=nq,observed=observed,variance=delta,authorized_delta=delta,control_result='VERIFIED',recorded_at=ts)
   c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,'INVENTORY_RECONCILIATION',reconciliation_id,'VERIFIED',ts))
   audit_event=event.event_id
   rr.append_state(c,reconciliation_id=reconciliation_id,asset_id=asset_id,state='RECONCILED',event_id=event.event_id,request_id=request_id,evidence_reference=evidence_reference,remaining=remaining,current=nq,observed=observed,variance=delta,authorized_delta=delta,control_result='RECONCILED',recorded_at=ts)
   rr.insert_final(c,(reconciliation_id,asset_id,event.event_id,request_id,f'RECONCILE:{request_id}',evidence_type,evidence_reference,1,observed,remaining,current,delta,delta,nq,reconciliation_reason,'RECONCILED',int(hist['history_id']),audit_event,ts,ts,ts))
   self._verify_event(c,event)
  return event
 def result(self,reconciliation_id):
  with self.database.connect() as c:
   r=self.repo.get(c,reconciliation_id)
   if not r:return None
   inv=c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=?',(r['asset_id'],)).fetchone(); ledger=self.remaining_quantity_truth(c,r['asset_id']); replay=int(c.execute('SELECT COUNT(*) FROM replay_defense_history WHERE request_id=?',(r['request_id'],)).fetchone()[0]); audit=int(c.execute("SELECT COUNT(*) FROM audit_events WHERE event_id=? AND authority_type='INVENTORY_RECONCILIATION'",(r['event_id'],)).fetchone()[0])
   return dict(r)|{'authoritative_quantity':int(inv['quantity']),'ledger_quantity':ledger,'ledger_result':'RECONCILED' if ledger==int(inv['quantity']) else 'BLOCKED','replay_count':replay,'audit_count':audit}
