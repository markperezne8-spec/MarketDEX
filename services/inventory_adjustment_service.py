from uuid import uuid4
from .base_service import AuthoritativeService
class InventoryAdjustmentService(AuthoritativeService):
 service_name='inventory_service'
 def __init__(self,database,events,assets,inventory,availability): super().__init__(database,events); self.assets,self.inventory,self.availability=assets,inventory,availability
 def available_quantity(self,asset_id): return self.availability.available_quantity(asset_id)
 def eligibility(self,*,asset_id,adjustment_type,adjustment_quantity,evidence_type,evidence_reference,evidence_complete,request_id):
  try:q=int(adjustment_quantity)
  except:q=0
  typ=str(adjustment_type).strip().upper(); complete=bool(evidence_complete) and bool(str(evidence_type).strip()) and bool(str(evidence_reference).strip())
  with self.database.connect() as c: asset=self.assets.get(c,str(asset_id).strip()) if str(asset_id).strip() else None
  av=self.available_quantity(str(asset_id).strip()) if asset is not None else 0; ok=asset is not None and complete and bool(str(request_id).strip()) and typ in ('DAMAGE','LOSS') and q>0 and q<=av
  return {'adjustment_eligible':ok,'control_result':'CONTROLLED' if ok else 'BLOCKED','available_quantity':av}
 def execute(self,*,request_id,adjustment_id,asset_id,adjustment_type,adjustment_quantity,evidence_type,evidence_reference,evidence_complete):
  typ=str(adjustment_type).strip().upper(); q=int(adjustment_quantity); gate=self.eligibility(asset_id=asset_id,adjustment_type=typ,adjustment_quantity=q,evidence_type=evidence_type,evidence_reference=evidence_reference,evidence_complete=evidence_complete,request_id=request_id)
  if not gate['adjustment_eligible']: raise ValueError('Adjustment authority BLOCKED')
  payload={'adjustment_id':adjustment_id,'asset_id':asset_id,'adjustment_type':typ,'adjustment_quantity':q,'evidence_type':evidence_type,'evidence_reference':evidence_reference,'evidence_complete':True}; event=self._new_event(typ,request_id,payload); movement_id=f'MOV-{uuid4()}'
  with self.database.transaction() as c:
   inv=self.inventory.get(c,asset_id); active=int(self.availability.active_allocation_quantity(asset_id,c)); available=(int(inv['quantity']) if inv else 0)-active
   if q<=0 or q>available: raise ValueError('Stale or insufficient authoritative available quantity')
   self._append_event_and_audit(c,event,f'apply_{typ.lower()}_adjustment'); nq,ncost=self.inventory.apply(c,asset_id=asset_id,quantity_delta=-q,cost_delta_minor=0,event_id=event.event_id,recorded_at=event.committed_at)
   c.execute('INSERT INTO inventory_movements VALUES (?,?,?,?,?,?,?)',(movement_id,asset_id,event.event_id,-q,0,typ,event.committed_at)); c.execute('INSERT INTO inventory_adjustments VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(adjustment_id,asset_id,typ,q,evidence_type,evidence_reference,1,request_id,f'{typ}:{request_id}',movement_id,event.event_id,'CONTROLLED',event.committed_at,event.committed_at)); c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,typ,adjustment_id,'VERIFIED',event.committed_at)); self._verify_event(c,event)
   row=self.inventory.get(c,asset_id); expected=int(c.execute('SELECT COALESCE(SUM(quantity_delta),0) FROM inventory_history WHERE asset_id=?',(asset_id,)).fetchone()[0])
   if int(row['quantity'])!=nq or expected!=nq: raise RuntimeError('Movement ledger reconciliation mismatch')
  return event
