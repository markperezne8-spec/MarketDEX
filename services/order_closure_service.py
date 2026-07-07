from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from services.base_service import AuthoritativeService


class OrderClosureBlocked(RuntimeError): pass


class OrderClosureService(AuthoritativeService):
    service_name='order_closure_service'
    def __init__(self,path):
        self.path=Path(path); self.database=DatabaseManager(self.path); self.database.initialize(); self.events=EventRepository(); super().__init__(self.database,self.events)

    def close(self,*,closure_id,sale_id,settlement_id,product_id,asset_id,listing_id,allocation_id,marketplace,closure_request_id,intent):
        vals=(closure_id,sale_id,settlement_id,product_id,asset_id,listing_id,allocation_id,marketplace,closure_request_id)
        if not all(str(v).strip() for v in vals) or str(intent).upper()!='CLOSE': raise OrderClosureBlocked('Explicit complete order closure authority required')
        payload={'closure_id':closure_id,'sale_id':sale_id,'settlement_id':settlement_id,'product_id':product_id,'asset_id':asset_id,'listing_id':listing_id,'allocation_id':allocation_id,'marketplace':marketplace}
        event=self._new_event('ORDER_CLOSE',closure_request_id,payload)
        with self.database.read_connection() as c:
            prior=c.execute('SELECT * FROM event_identity WHERE request_id=?',(closure_request_id,)).fetchone()
            if prior:
                row=c.execute('SELECT * FROM order_closures WHERE closure_request_id=?',(closure_request_id,)).fetchone()
                if row and row['closure_id']==closure_id and prior['payload_sha256']==event.payload_sha256:
                    self._replay(prior); return dict(row)
                raise OrderClosureBlocked('Closure request identity mismatch')
        with self.database.transaction() as c:
            sale=c.execute("SELECT * FROM sales WHERE sale_id=? AND asset_id=? AND state='COMPLETED'",(sale_id,asset_id)).fetchone()
            settlement=c.execute("SELECT * FROM settlement_executions WHERE settlement_id=? AND sale_id=? AND settlement_result='SETTLED'",(settlement_id,sale_id)).fetchone()
            link=c.execute("SELECT 1 FROM inventory_product_links WHERE product_id=? AND asset_id=? AND state='LINKED'",(product_id,asset_id)).fetchone()
            listing=c.execute("SELECT 1 FROM marketplace_listing_identities WHERE listing_identity_id=? AND product_id=? AND marketplace=?",(listing_id,product_id,marketplace)).fetchone()
            allocation=c.execute("SELECT 1 FROM marketplace_publication_allocations WHERE allocation_id=? AND asset_id=? AND publication_identity=? AND marketplace=?",(allocation_id,asset_id,listing_id,marketplace)).fetchone()
            sold=c.execute("SELECT 1 FROM publication_lifecycle_events WHERE allocation_id=? AND sale_id=? AND sale_event_id=? AND marketplace=? AND event_type='SOLD_CONVERSION'",(allocation_id,sale_id,sale['created_event_id'] if sale else '',marketplace)).fetchone()
            if not all((sale,settlement,link,listing,allocation,sold)): raise OrderClosureBlocked('Accepted product-aware SETTLED sale lineage required')
            if settlement['settlement_platform']!=marketplace: raise OrderClosureBlocked('Settlement marketplace lineage mismatch')
            if c.execute('SELECT 1 FROM order_closures WHERE sale_id=? OR settlement_id=?',(sale_id,settlement_id)).fetchone(): raise OrderClosureBlocked('Second order closure blocked')
            inv=c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=?',(asset_id,)).fetchone()['quantity']; sales=c.execute('SELECT COUNT(*) n FROM sales').fetchone()['n']; fin=c.execute('SELECT COUNT(*) n FROM sales_financial_history').fetchone()['n']; settlements=c.execute('SELECT COUNT(*) n FROM settlement_executions').fetchone()['n']; soldn=c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n']
            self._append_event_and_audit(c,event,'close_order')
            c.execute('INSERT INTO order_closures VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(*vals,event.event_id,'CLOSED',event.committed_at))
            c.execute('INSERT INTO order_closure_history(closure_id,sale_id,settlement_id,closure_event_id,closure_result,recorded_at) VALUES (?,?,?,?,?,?)',(closure_id,sale_id,settlement_id,event.event_id,'CLOSED',event.committed_at))
            c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,'ORDER_CLOSE',closure_id,'VERIFIED',event.committed_at)); self._verify_event(c,event)
            if c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=?',(asset_id,)).fetchone()['quantity']!=inv or c.execute('SELECT COUNT(*) n FROM sales').fetchone()['n']!=sales or c.execute('SELECT COUNT(*) n FROM sales_financial_history').fetchone()['n']!=fin or c.execute('SELECT COUNT(*) n FROM settlement_executions').fetchone()['n']!=settlements or c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n']!=soldn: raise RuntimeError('Order closure mutated preserved authority')
        return self.get(closure_id)

    def _replay(self,prior):
        with self.database.transaction() as c:c.execute("INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES (?,?,?,?, 'BLOCKED',?)",(prior['request_id'],prior['event_id'],'ORDER_CLOSE',prior['payload_sha256'],prior['committed_at']))
    def get(self,closure_id):
        with self.database.read_connection() as c:
            r=c.execute('SELECT * FROM order_closures WHERE closure_id=?',(closure_id,)).fetchone(); h=c.execute('SELECT COUNT(*) n FROM order_closure_history WHERE closure_id=?',(closure_id,)).fetchone()['n']
            if not r or h!=1: raise OrderClosureBlocked('Order closure reconstruction failed')
            return dict(r)
