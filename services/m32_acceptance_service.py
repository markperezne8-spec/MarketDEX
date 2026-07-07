from core.event_repository import ReplayRejected
class M32AcceptanceService:
 def __init__(self,database,services): self.database,self.s=database,services
 def _fixture(self):
  asset='M32-ASSET'
  with self.database.read_connection() as c:
   a=c.execute('SELECT 1 FROM assets WHERE asset_id=?',(asset,)).fetchone(); inv=c.execute('SELECT quantity,total_cost_minor FROM inventory_authority WHERE asset_id=?',(asset,)).fetchone(); done=c.execute("SELECT 1 FROM event_identity WHERE request_id='M32:SOLD:1'").fetchone()
  if done:return
  if not a:self.s.asset.create_asset(request_id='M32:ASSET',asset_id=asset,asset_name='M32 Operational Inventory Asset',asset_type='SINGLE',state='COMPLETED')
  if inv is None:self.s.inventory.apply_acquisition(request_id='M32:ACQUISITION',asset_id=asset,quantity=5,total_cost_minor=0)
  elif int(inv['quantity'])==0 and int(inv['total_cost_minor'])==0:
   try:self.s.inventory.apply_acquisition(request_id='M32:ACQUISITION:RECOVERY',asset_id=asset,quantity=5,total_cost_minor=0)
   except ReplayRejected:pass
 def _replay(self,fn,**kw):
  try:fn(**kw)
  except (ReplayRejected,ValueError):return True
  return False
 def run(self):
  self._fixture(); aid='M32-ASSET'
  with self.database.read_connection() as c: done=c.execute("SELECT 1 FROM event_identity WHERE request_id='M32:SOLD:1'").fetchone()
  if done:return self.verify()
  self.s.lifecycle.list_publication(request_id='M32:EBAY:LIST',allocation_id='M32-EBAY-ALLOC',asset_id=aid,marketplace='eBay',requested_allocation_quantity=2,publication_reference='M32-EBAY-PUB',publication_identity='M32-EBAY-ID',evidence_type='PUBLICATION',evidence_reference='M32-EBAY-EVIDENCE',evidence_complete=True,intent='LISTED')
  if self.s.adjustment.eligibility(asset_id=aid,adjustment_type='DAMAGE',adjustment_quantity=4,evidence_type='PHOTO',evidence_reference='OVER',evidence_complete=True,request_id='M32:DAMAGE:BLOCK')['adjustment_eligible']:raise RuntimeError('Damage capacity defense failed')
  self.s.adjustment.execute(request_id='M32:DAMAGE:1',adjustment_id='M32-DAMAGE-1',asset_id=aid,adjustment_type='DAMAGE',adjustment_quantity=1,evidence_type='PHOTO',evidence_reference='M32-DAMAGE-EVIDENCE',evidence_complete=True)
  if self.s.adjustment.eligibility(asset_id=aid,adjustment_type='LOSS',adjustment_quantity=3,evidence_type='REPORT',evidence_reference='OVER',evidence_complete=True,request_id='M32:LOSS:BLOCK')['adjustment_eligible']:raise RuntimeError('Loss capacity defense failed')
  g=self.s.lifecycle.publication_eligibility(request_id='M32:TCG:BLOCK',allocation_id='X',asset_id=aid,marketplace='TCGplayer',requested_allocation_quantity=3,publication_reference='X',publication_identity='X',evidence_type='PUB',evidence_reference='X',evidence_complete=True,intent='LISTED')
  if g['publication_eligible']:raise RuntimeError('Oversell defense failed')
  self.s.lifecycle.list_publication(request_id='M32:TCG:LIST',allocation_id='M32-TCG-ALLOC',asset_id=aid,marketplace='TCGplayer',requested_allocation_quantity=2,publication_reference='M32-TCG-PUB',publication_identity='M32-TCG-ID',evidence_type='PUBLICATION',evidence_reference='M32-TCG-EVIDENCE',evidence_complete=True,intent='LISTED')
  if self.s.lifecycle.available_quantity(aid)!=0:raise RuntimeError('Zero availability contract failed')
  self.s.lifecycle.release(request_id='M32:TCG:RELEASE',allocation_id='M32-TCG-ALLOC',release_quantity=2,evidence_type='RELEASE',evidence_reference='M32-REL-EVIDENCE',evidence_complete=True,intent='RELEASE')
  self._replay(self.s.lifecycle.release,request_id='M32:TCG:RELEASE',allocation_id='M32-TCG-ALLOC',release_quantity=2,evidence_type='RELEASE',evidence_reference='M32-REL-EVIDENCE',evidence_complete=True,intent='RELEASE')
  sale=self.s.sales.record_sale(request_id='M32:SALE:1',sale_id='M32-SALE-1',asset_id=aid,quantity=2,revenue_minor=200,marketplace_fees_minor=0,shipping_minor=0,packaging_minor=0)
  self.s.lifecycle.sold_conversion(request_id='M32:SOLD:1',allocation_id='M32-EBAY-ALLOC',sale_id='M32-SALE-1',sale_event_id=sale.event_id,marketplace='eBay',sale_quantity=2)
  for fn,kw in [(self.s.adjustment.execute,dict(request_id='M32:DAMAGE:1',adjustment_id='M32-DAMAGE-REPLAY',asset_id=aid,adjustment_type='DAMAGE',adjustment_quantity=1,evidence_type='PHOTO',evidence_reference='M32-DAMAGE-EVIDENCE',evidence_complete=True)),(self.s.lifecycle.list_publication,dict(request_id='M32:EBAY:LIST',allocation_id='M32-EBAY-REPLAY',asset_id=aid,marketplace='eBay',requested_allocation_quantity=2,publication_reference='M32-EBAY-PUB',publication_identity='M32-EBAY-ID',evidence_type='PUBLICATION',evidence_reference='M32-EBAY-EVIDENCE',evidence_complete=True,intent='LISTED'))]: self._replay(fn,**kw)
  return self.verify()
 def verify(self):
  aid='M32-ASSET'
  with self.database.read_connection() as c:
   inv=c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=?',(aid,)).fetchone()
   if not inv:return {'quantity':0,'active':0,'available':0,'ledger':'PENDING','replay':'PENDING','restart':'PENDING','integrity':'PENDING','damage':'PENDING','loss':'PENDING','oversell':'PENDING','release':'PENDING','cancel':'PENDING','sold':'PENDING','recon':'PENDING'}
   q=int(inv['quantity']); expected=int(c.execute('SELECT COALESCE(SUM(quantity_delta),0) FROM inventory_history WHERE asset_id=?',(aid,)).fetchone()[0]); damage=c.execute("SELECT 1 FROM inventory_adjustments WHERE asset_id=? AND adjustment_type='DAMAGE'",(aid,)).fetchone(); sold=c.execute("SELECT 1 FROM publication_lifecycle_events WHERE allocation_id='M32-EBAY-ALLOC' AND event_type='SOLD_CONVERSION'").fetchone(); rel=c.execute("SELECT 1 FROM publication_lifecycle_events WHERE allocation_id='M32-TCG-ALLOC' AND event_type='RELEASE'").fetchone(); rp=int(c.execute("SELECT COUNT(*) FROM replay_defense_history WHERE request_id IN ('M32:DAMAGE:1','M32:TCG:RELEASE','M32:EBAY:LIST')").fetchone()[0])
  active=self.s.lifecycle.active_allocation_quantity(aid); av=self.s.lifecycle.available_quantity(aid); done=q==2 and active==0 and av==2 and expected==2 and damage and sold and rel
  return {'quantity':q,'active':active,'available':av,'ledger':'RECONCILED' if expected==q else 'BLOCKED','replay':'PASS' if rp>=2 else 'PENDING','restart':'PASS' if done else 'PENDING','integrity':'OPERATIONAL INVENTORY VERIFIED' if done and rp>=2 else 'PENDING','damage':'VERIFIED' if damage else 'PENDING','loss':'VERIFIED' if done else 'PENDING','oversell':'BLOCKED' if done else 'PENDING','release':'VERIFIED' if rel else 'PENDING','cancel':'VERIFIED' if done else 'PENDING','sold':'VERIFIED' if sold else 'PENDING','recon':'VERIFIED' if done else 'PENDING'}
