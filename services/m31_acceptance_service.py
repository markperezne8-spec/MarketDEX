from core.event_repository import ReplayRejected
class M31AcceptanceService:
 def __init__(self,database,services): self.database,self.s=database,services
 def _fixture(self):
  with self.database.read_connection() as c:
   asset=c.execute("SELECT 1 FROM assets WHERE asset_id='M31-ASSET'").fetchone(); inv=c.execute("SELECT quantity,total_cost_minor FROM inventory_authority WHERE asset_id='M31-ASSET'").fetchone(); final=c.execute("SELECT 1 FROM inventory_reconciliations WHERE reconciliation_id='M31-REC-1'").fetchone()
  if final:return
  if not asset:self.s.asset.create_asset(request_id='M31:ASSET',asset_id='M31-ASSET',asset_name='M31 Reconciliation Acceptance Asset',asset_type='SINGLE',state='COMPLETED')
  if inv is None:self.s.inventory.apply_acquisition(request_id='M31:ACQUISITION',asset_id='M31-ASSET',quantity=3,total_cost_minor=0)
  elif int(inv['quantity'])==0 and int(inv['total_cost_minor'])==0:
   try:self.s.inventory.apply_acquisition(request_id='M31:ACQUISITION:RECOVERY',asset_id='M31-ASSET',quantity=3,total_cost_minor=0)
   except ReplayRejected:pass
 def run(self):
  self._fixture()
  with self.database.read_connection() as c: already=c.execute("SELECT 1 FROM inventory_reconciliations WHERE reconciliation_id='M31-REC-1'").fetchone()
  if already:return self.verify()
  blocked=self.s.reconciliation.evaluate(asset_id='M31-ASSET',evidence_type='PHYSICAL_COUNT',evidence_reference='M31-EVIDENCE-1',evidence_complete=False,observed_quantity=2,reconciliation_reason='VERIFIED PHYSICAL COUNT VARIANCE',request_id='M31:RECONCILE:1',explicit_intent='RECONCILE')
  if blocked.get('eligible'):raise RuntimeError('Incomplete evidence did not fail closed')
  with self.database.read_connection() as c:q=int(c.execute("SELECT quantity FROM inventory_authority WHERE asset_id='M31-ASSET'").fetchone()[0])
  if q!=3: raise RuntimeError('Blocked reconciliation mutated inventory')
  try:self.s.reconciliation.reconcile(reconciliation_id='M31-REC-1',asset_id='M31-ASSET',evidence_type='PHYSICAL_COUNT',evidence_reference='M31-EVIDENCE-1',evidence_complete=True,observed_quantity=2,reconciliation_reason='VERIFIED PHYSICAL COUNT VARIANCE',request_id='M31:RECONCILE:1',explicit_intent='RECONCILE')
  except ReplayRejected:pass
  try:self.s.reconciliation.reconcile(reconciliation_id='M31-REC-1',asset_id='M31-ASSET',evidence_type='PHYSICAL_COUNT',evidence_reference='M31-EVIDENCE-1',evidence_complete=True,observed_quantity=2,reconciliation_reason='VERIFIED PHYSICAL COUNT VARIANCE',request_id='M31:RECONCILE:1',explicit_intent='RECONCILE')
  except ReplayRejected:pass
  else:raise RuntimeError('Replay created second reconciliation mutation')
  return self.verify()
 def verify(self):
  r=self.s.reconciliation.result('M31-REC-1')
  if not r:return {'remaining':3,'quantity':0,'observed':0,'delta':0,'ledger':'PENDING','state':'PENDING','replay':0,'history':0,'audit':0,'movement':0}
  with self.database.read_connection() as c:
   history=int(c.execute("SELECT COUNT(*) FROM reconciliation_history WHERE reconciliation_id='M31-REC-1'").fetchone()[0]); movement=int(c.execute("SELECT COUNT(*) FROM inventory_history WHERE event_id=?",(r['event_id'],)).fetchone()[0])
  return {'remaining':int(r['remaining_quantity_truth']),'quantity':r['authoritative_quantity'],'observed':int(r['observed_quantity']),'delta':int(r['authorized_delta']),'ledger':r['ledger_result'],'state':r['reconciliation_state'],'replay':r['replay_count'],'history':history,'audit':r['audit_count'],'movement':movement}
