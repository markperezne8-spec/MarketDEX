from .base_service import AuthoritativeService
class SalesService(AuthoritativeService):
 service_name='sales_service'
 def __init__(self,database,events,assets,inventory):super().__init__(database,events); self.assets,self.inventory=assets,inventory
 def record_sale(self,*,request_id,sale_id,asset_id,quantity,revenue_minor,marketplace_fees_minor,shipping_minor,packaging_minor):
  q=int(quantity); values=[int(revenue_minor),int(marketplace_fees_minor),int(shipping_minor),int(packaging_minor)]; payload={'sale_id':sale_id,'asset_id':asset_id,'quantity':q,'revenue_minor':values[0],'marketplace_fees_minor':values[1],'shipping_minor':values[2],'packaging_minor':values[3]}; event=self._new_event('SALE',request_id,payload)
  with self.database.transaction() as c:
   source=self.inventory.get(c,asset_id)
   if source is None or q<=0 or q>int(source['quantity']):raise ValueError('Sale quantity exceeds available inventory')
   cogs=int(source['total_cost_minor']) if q==int(source['quantity']) else int(source['total_cost_minor'])*q//int(source['quantity']); revenue,fees,shipping,packaging=values; profit=revenue-fees-shipping-packaging-cogs
   self._append_event_and_audit(c,event,'record_sale'); c.execute("INSERT INTO sales(sale_id,asset_id,quantity,revenue_minor,marketplace_fees_minor,shipping_minor,packaging_minor,cogs_minor,profit_minor,state,created_event_id,created_at) VALUES (?,?,?,?,?,?,?,?,?,'COMPLETED',?,?)",(sale_id,asset_id,q,revenue,fees,shipping,packaging,cogs,profit,event.event_id,event.committed_at)); self.inventory.apply(c,asset_id=asset_id,quantity_delta=-q,cost_delta_minor=-cogs,event_id=event.event_id,recorded_at=event.committed_at); c.execute('INSERT INTO sales_financial_history(event_id,sale_id,revenue_minor,marketplace_fees_minor,shipping_minor,packaging_minor,cogs_minor,profit_minor,recorded_at) VALUES (?,?,?,?,?,?,?,?,?)',(event.event_id,sale_id,revenue,fees,shipping,packaging,cogs,profit,event.committed_at)); self._verify_event(c,event)
  return event
