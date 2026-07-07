from core.authority import Authority,AuthorityBlocked
class BusinessService(Authority):
 def create_asset_and_acquire(self,*,asset_id,name,quantity,total_cost_minor):
  with self.db.transaction() as c:
   request_id=f'{asset_id}:CREATE'; payload={'asset_id':asset_id,'name':name}
   eid,ts=self.event(c,'ASSET_CREATE',request_id,payload)
   asset_columns={row['name'] for row in c.execute('PRAGMA table_info(assets)').fetchall()}
   if {'asset_name','asset_type','state','created_event_id','created_at'}.issubset(asset_columns):
    # M20-M29 persistent authority schema compatibility. Mirror the bootstrap event
    # into the accepted immutable event identity table before creating the asset.
    if c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='event_identity'").fetchone():
     source=c.execute('SELECT payload,payload_sha,committed_at FROM events WHERE event_id=?',(eid,)).fetchone()
     c.execute('INSERT INTO event_identity(event_id,event_type,request_id,occurred_at,committed_at,payload_json,payload_sha256) VALUES (?,?,?,?,?,?,?)',(eid,'ASSET_CREATE',request_id,ts,ts,source['payload'],source['payload_sha']))
    c.execute('INSERT INTO assets(asset_id,asset_name,asset_type,state,created_event_id,created_at) VALUES (?,?,?,?,?,?)',(asset_id,name,'SINGLE','COMPLETED',eid,ts))
   else:
    c.execute('INSERT INTO assets(asset_id,name,created_event_id) VALUES (?,?,?)',(asset_id,name,eid))
   self.audit(c,eid,'ASSET',asset_id,ts)
  with self.db.transaction() as c:
   eid,ts=self.event(c,'ACQUISITION',f'{asset_id}:ACQUIRE',{'asset_id':asset_id,'quantity':quantity,'total_cost_minor':total_cost_minor}); c.execute('INSERT INTO inventory VALUES (?,?,?,?)',(asset_id,int(quantity),int(total_cost_minor),eid)); c.execute('INSERT INTO inventory_history(event_id,asset_id,quantity_delta,cost_delta_minor,resulting_quantity,resulting_cost_minor,recorded_at) VALUES (?,?,?,?,?,?,?)',(eid,asset_id,int(quantity),int(total_cost_minor),int(quantity),int(total_cost_minor),ts)); self.audit(c,eid,'ACQUISITION',asset_id,ts)
 def sale(self,*,request_id,sale_id,asset_id,marketplace,quantity,revenue_minor,fees_minor,shipping_minor,packaging_minor):
  q=int(quantity)
  with self.db.transaction() as c:
   inv=c.execute('SELECT * FROM inventory WHERE asset_id=?',(asset_id,)).fetchone()
   if inv is None or q<=0 or q>int(inv['quantity']): raise AuthorityBlocked('M24 sale authority BLOCKED')
   eid,ts=self.event(c,'SALE',request_id,{'sale_id':sale_id,'asset_id':asset_id,'marketplace':marketplace,'quantity':q,'revenue_minor':revenue_minor,'fees_minor':fees_minor,'shipping_minor':shipping_minor,'packaging_minor':packaging_minor})
   cogs=int(inv['total_cost_minor']) if q==int(inv['quantity']) else int(inv['total_cost_minor'])*q//int(inv['quantity']); profit=int(revenue_minor)-int(fees_minor)-int(shipping_minor)-int(packaging_minor)-cogs; nq=int(inv['quantity'])-q; nc=int(inv['total_cost_minor'])-cogs
   c.execute('INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(sale_id,asset_id,marketplace,q,int(revenue_minor),int(fees_minor),int(shipping_minor),int(packaging_minor),cogs,profit,eid,ts)); c.execute('UPDATE inventory SET quantity=?,total_cost_minor=?,last_event_id=? WHERE asset_id=?',(nq,nc,eid,asset_id)); c.execute('INSERT INTO inventory_history(event_id,asset_id,quantity_delta,cost_delta_minor,resulting_quantity,resulting_cost_minor,recorded_at) VALUES (?,?,?,?,?,?,?)',(eid,asset_id,-q,-cogs,nq,nc,ts)); c.execute('INSERT INTO sale_financial_history(sale_id,event_id,profit_minor,recorded_at) VALUES (?,?,?,?)',(sale_id,eid,profit,ts)); self.audit(c,eid,'SALE',sale_id,ts)
  return eid
