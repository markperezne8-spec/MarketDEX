from .base_service import AuthoritativeService
from repositories.asset_repository import AssetRepository
from repositories.inventory_repository import InventoryRepository

class SalesService(AuthoritativeService):
    service_name='sales_service'
    def __init__(self,database,events,assets=None,inventory=None):
        super().__init__(database,events)
        self.assets=assets or AssetRepository()
        self.inventory=inventory or InventoryRepository()

    def record_sale(self,*,request_id,sale_id,asset_id,quantity,revenue_minor,marketplace_fees_minor,shipping_minor,packaging_minor):
        if not all(str(x).strip() for x in (request_id,sale_id,asset_id)):
            raise ValueError('Sale evidence is incomplete')
        quantity=int(quantity)
        values=[int(revenue_minor),int(marketplace_fees_minor),int(shipping_minor),int(packaging_minor)]
        if quantity<=0:
            raise ValueError('Sale quantity must be greater than zero')
        if any(v<0 for v in values):
            raise ValueError('Financial evidence cannot be negative')
        payload={'sale_id':sale_id,'asset_id':asset_id,'quantity':quantity,'revenue_minor':values[0],
                 'marketplace_fees_minor':values[1],'shipping_minor':values[2],'packaging_minor':values[3]}
        event=self._new_event('SALE',request_id,payload)
        with self.database.transaction() as c:
            source=self.inventory.get(c,asset_id)
            if source is None or int(source['quantity'])<=0:
                raise ValueError('Zero available inventory is unsaleable')
            if quantity>int(source['quantity']):
                raise ValueError('Sale quantity exceeds available inventory')
            if c.execute('SELECT 1 FROM sales WHERE sale_id=?',(sale_id,)).fetchone():
                raise ValueError('Sale identity already exists')
            cogs=int(source['total_cost_minor']) if quantity==int(source['quantity']) else (int(source['total_cost_minor'])*quantity)//int(source['quantity'])
            revenue,fees,shipping,packaging=values
            profit=revenue-fees-shipping-packaging-cogs
            self._append_event_and_audit(c,event,'record_sale')
            c.execute("""INSERT INTO sales(sale_id,asset_id,quantity,revenue_minor,marketplace_fees_minor,shipping_minor,packaging_minor,cogs_minor,profit_minor,state,created_event_id,created_at)
                         VALUES (?,?,?,?,?,?,?,?,?,'COMPLETED',?,?)""",
                      (sale_id,asset_id,quantity,revenue,fees,shipping,packaging,cogs,profit,event.event_id,event.committed_at))
            self.inventory.apply(c,asset_id=asset_id,quantity_delta=-quantity,cost_delta_minor=-cogs,event_id=event.event_id,recorded_at=event.committed_at)
            c.execute("""INSERT INTO sales_financial_history(event_id,sale_id,revenue_minor,marketplace_fees_minor,shipping_minor,packaging_minor,cogs_minor,profit_minor,recorded_at)
                         VALUES (?,?,?,?,?,?,?,?,?)""",
                      (event.event_id,sale_id,revenue,fees,shipping,packaging,cogs,profit,event.committed_at))
            row=c.execute('SELECT * FROM sales WHERE sale_id=?',(sale_id,)).fetchone()
            expected=int(row['revenue_minor'])-int(row['marketplace_fees_minor'])-int(row['shipping_minor'])-int(row['packaging_minor'])-int(row['cogs_minor'])
            if expected!=int(row['profit_minor']):
                raise RuntimeError('Post-write financial truth verification failed')
            remaining=self.inventory.get(c,asset_id)
            if int(remaining['quantity'])<0 or int(remaining['total_cost_minor'])<0:
                raise RuntimeError('Post-write inventory verification failed')
            self._verify_event(c,event)
        return event
