from core.event_repository import ReplayRejected
from .marketplace_lifecycle_service import AuthorityBlocked
class M30AcceptanceService:
 def __init__(self,database,services):self.database,self.s=database,services
 def run(self):
  with self.database.connect() as c:
   exists=c.execute("SELECT 1 FROM assets WHERE asset_id='M30-ASSET'").fetchone()
   inventory=c.execute("SELECT quantity FROM inventory_authority WHERE asset_id='M30-ASSET'").fetchone()
  if not exists:
   self.s.asset.create_asset(request_id='M30:ASSET',asset_id='M30-ASSET',asset_name='M30 Publication Lifecycle Test Asset',asset_type='SINGLE',state='COMPLETED')
  if inventory is None or int(inventory['quantity']) == 0:
   self.s.inventory.apply_acquisition(request_id='M30:ACQUISITION',asset_id='M30-ASSET',quantity=3,total_cost_minor=300)
  self._once(self.s.lifecycle.list_publication,request_id='M30:LIST:EBAY',allocation_id='M30-ALLOC-EBAY',asset_id='M30-ASSET',marketplace='eBay',requested_allocation_quantity=2,publication_reference='EBAY-LIST-001',publication_identity='EBAY:PUB:001',evidence_type='PUBLICATION',evidence_reference='EBAY-EVIDENCE',evidence_complete=True,intent='LISTED')
  blocked=False
  try:self.s.lifecycle.list_publication(request_id='M30:LIST:TCG:BLOCK',allocation_id='M30-ALLOC-TCG-BLOCK',asset_id='M30-ASSET',marketplace='TCGplayer',requested_allocation_quantity=2,publication_reference='TCG-BLOCK',publication_identity='TCG:PUB:BLOCK',evidence_type='PUBLICATION',evidence_reference='TCG-EVIDENCE-BLOCK',evidence_complete=True,intent='LISTED')
  except AuthorityBlocked:blocked=True
  if not blocked:raise RuntimeError('Cross-channel oversell did not fail closed')
  self._once(self.s.lifecycle.list_publication,request_id='M30:LIST:TCG',allocation_id='M30-ALLOC-TCG',asset_id='M30-ASSET',marketplace='TCGplayer',requested_allocation_quantity=1,publication_reference='TCG-LIST-001',publication_identity='TCG:PUB:001',evidence_type='PUBLICATION',evidence_reference='TCG-EVIDENCE',evidence_complete=True,intent='LISTED')
  self._once(self.s.lifecycle.release,request_id='M30:RELEASE:1',allocation_id='M30-ALLOC-EBAY',release_quantity=1,evidence_type='RELEASE',evidence_reference='RELEASE-EVIDENCE',evidence_complete=True,intent='RELEASE'); self._replay(self.s.lifecycle.release,request_id='M30:RELEASE:1',allocation_id='M30-ALLOC-EBAY',release_quantity=1,evidence_type='RELEASE',evidence_reference='RELEASE-EVIDENCE',evidence_complete=True,intent='RELEASE')
  self._once(self.s.lifecycle.cancel,request_id='M30:CANCEL:1',allocation_id='M30-ALLOC-TCG',evidence_type='CANCELLATION',evidence_reference='CANCEL-EVIDENCE',evidence_complete=True,intent='CANCELLATION'); self._replay(self.s.lifecycle.cancel,request_id='M30:CANCEL:1',allocation_id='M30-ALLOC-TCG',evidence_type='CANCELLATION',evidence_reference='CANCEL-EVIDENCE',evidence_complete=True,intent='CANCELLATION')
  with self.database.connect() as c:sale=c.execute("SELECT * FROM sales WHERE sale_id='M30-SALE-1'").fetchone()
  sale_event=sale['created_event_id'] if sale else self.s.sales.record_sale(request_id='M30:SALE:1',sale_id='M30-SALE-1',asset_id='M30-ASSET',quantity=1,revenue_minor=1000,marketplace_fees_minor=100,shipping_minor=50,packaging_minor=25).event_id
  self._once(self.s.lifecycle.sold_conversion,request_id='M30:SOLD:1',allocation_id='M30-ALLOC-EBAY',sale_id='M30-SALE-1',sale_event_id=sale_event,marketplace='eBay',sale_quantity=1); self._replay(self.s.lifecycle.sold_conversion,request_id='M30:SOLD:1',allocation_id='M30-ALLOC-EBAY',sale_id='M30-SALE-1',sale_event_id=sale_event,marketplace='eBay',sale_quantity=1)
  return self.verify()
 def _once(self,fn,**k):
  try:return fn(**k)
  except ReplayRejected:return None
 def _replay(self,fn,**k):
  try:fn(**k)
  except ReplayRejected:return
  raise RuntimeError('Replay created second authoritative mutation')
 def verify(self):
  with self.database.connect() as c:
   row=c.execute("SELECT quantity FROM inventory_authority WHERE asset_id='M30-ASSET'").fetchone(); q=int(row[0]) if row else 0; active=self.s.lifecycle.active_allocation_quantity('M30-ASSET',c); available=self.s.lifecycle.available_quantity('M30-ASSET',c); lifecycle={r['event_type']:int(r['n']) for r in c.execute('SELECT event_type,COUNT(*) n FROM publication_lifecycle_events GROUP BY event_type').fetchall()}; ebay=c.execute("SELECT * FROM marketplace_publication_allocations WHERE allocation_id='M30-ALLOC-EBAY'").fetchone(); tcg=c.execute("SELECT * FROM marketplace_publication_allocations WHERE allocation_id='M30-ALLOC-TCG'").fetchone(); replays=int(c.execute("SELECT COUNT(*) FROM replay_defense_history WHERE request_id IN ('M30:RELEASE:1','M30:CANCEL:1','M30:SOLD:1')").fetchone()[0]); financial=int(c.execute("SELECT COUNT(*) FROM sales_financial_history WHERE sale_id='M30-SALE-1'").fetchone()[0]); audits=int(c.execute("SELECT COUNT(*) FROM audit_events WHERE authority_type IN ('LISTED','RELEASE','CANCELLATION','SOLD_CONVERSION')").fetchone()[0])
  return {'quantity':q,'active':active,'available':available,'lifecycle':lifecycle,'ebay_state':ebay['state'] if ebay else None,'tcg_state':tcg['state'] if tcg else None,'replays':replays,'financial':financial,'audits':audits}
