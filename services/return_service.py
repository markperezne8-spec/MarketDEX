from .base_service import AuthoritativeService
from repositories.inventory_repository import InventoryRepository
class ReturnService(AuthoritativeService):
 service_name='return_service'
 def __init__(self,database,events,inventory=None): super().__init__(database,events); self.inventory=inventory or InventoryRepository()
 def execute(self,*,request_id,return_id,sale_id,quantity,condition_evidence,restock_authorized,refund_minor):
  if not all(str(x).strip() for x in (request_id,return_id,sale_id)): raise ValueError('Return evidence or identity is incomplete')
  if not str(condition_evidence).strip(): raise ValueError('Condition evidence is required')
  quantity=int(quantity); refund_minor=int(refund_minor)
  if quantity<=0 or refund_minor<0: raise ValueError('Invalid return evidence')
  event=self._new_event('RETURN',request_id,{'return_id':return_id,'sale_id':sale_id,'quantity':quantity,'condition_evidence':condition_evidence,'restock_authorized':bool(restock_authorized),'refund_minor':refund_minor})
  with self.database.transaction() as c:
   sale=c.execute("SELECT * FROM sales WHERE sale_id=? AND state='COMPLETED'",(sale_id,)).fetchone()
   if sale is None: raise ValueError('No matched completed original sale')
   if quantity>int(sale['quantity']): raise ValueError('Return quantity exceeds original sale')
   if c.execute('SELECT 1 FROM returns WHERE return_id=?',(return_id,)).fetchone(): raise ValueError('Return identity already exists')
   original_event_id=sale['created_event_id']; restored_cost=0
   if restock_authorized:
    restored_cost=int(sale['cogs_minor']) if quantity==int(sale['quantity']) else (int(sale['cogs_minor'])*quantity)//int(sale['quantity'])
   profit_effect=-refund_minor+restored_cost
   self._append_event_and_audit(c,event,'execute_return')
   c.execute('INSERT INTO returns VALUES (?,?,?,?,?,?,?,?,?,?,?)',(return_id,sale_id,sale['asset_id'],quantity,condition_evidence,1 if restock_authorized else 0,refund_minor,restored_cost,profit_effect,event.event_id,event.committed_at))
   c.execute('INSERT INTO return_events(return_id,original_event_id,event_id,recorded_at) VALUES (?,?,?,?)',(return_id,original_event_id,event.event_id,event.committed_at))
   if restock_authorized:
    self.inventory.apply(c,asset_id=sale['asset_id'],quantity_delta=quantity,cost_delta_minor=restored_cost,event_id=event.event_id,recorded_at=event.committed_at)
    c.execute('INSERT INTO inventory_movements VALUES (?,?,?,?,?,?,?)',(f'MOV-{event.event_id}',sale['asset_id'],event.event_id,quantity,restored_cost,'RETURN_RESTOCK',event.committed_at))
   c.execute('INSERT INTO financial_events VALUES (?,?,?,?,?,?,?,?)',(f'FIN-{event.event_id}',event.event_id,original_event_id,sale_id,'RETURN_REFUND',-refund_minor,profit_effect,event.committed_at))
   c.execute('INSERT INTO event_history(event_id,original_event_id,authority_type,authority_id,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,original_event_id,'RETURN',return_id,event.committed_at))
   c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,'RETURN',return_id,'VERIFIED',event.committed_at))
   r=c.execute('SELECT * FROM returns WHERE return_id=?',(return_id,)).fetchone()
   if int(r['restored_cost_minor'])!=restored_cost or int(r['profit_restatement_minor'])!=profit_effect: raise RuntimeError('Return post-write verification failed')
   self._verify_event(c,event)
  return event
