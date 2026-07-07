from .base_service import AuthoritativeService

class IntegrationService(AuthoritativeService):
    service_name='integration_service'
    def __init__(self,database,events,services):
        super().__init__(database,events); self.services=services

    def available_quantity(self,asset_id):
        with self.database.connect() as c:
            inv=c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=?',(asset_id,)).fetchone()
            qty=int(inv['quantity']) if inv else 0
            allocated=c.execute("SELECT COALESCE(SUM(allocated_quantity),0) n FROM marketplace_allocations WHERE asset_id=? AND state='ACTIVE'",(asset_id,)).fetchone()['n']
        return qty-int(allocated)

    def allocate(self,*,request_id,allocation_id,asset_id,marketplace,allocated_quantity,publication_reference):
        q=int(allocated_quantity)
        if not all(str(x).strip() for x in (request_id,allocation_id,asset_id,marketplace)) or q<=0:
            raise ValueError('Allocation evidence is incomplete')
        event=self._new_event('MARKETPLACE_ALLOCATION',request_id,{'allocation_id':allocation_id,'asset_id':asset_id,'marketplace':marketplace,'allocated_quantity':q,'publication_reference':publication_reference})
        with self.database.transaction() as c:
            inv=c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=?',(asset_id,)).fetchone()
            active=c.execute("SELECT COALESCE(SUM(allocated_quantity),0) n FROM marketplace_allocations WHERE asset_id=? AND state='ACTIVE'",(asset_id,)).fetchone()['n']
            if inv is None or q > int(inv['quantity'])-int(active): raise ValueError('Cross-channel allocation exceeds authoritative available quantity')
            self._append_event_and_audit(c,event,'allocate_marketplace')
            c.execute('INSERT INTO marketplace_allocations VALUES (?,?,?,?,?,?,?,?)',(allocation_id,asset_id,marketplace,q,'ACTIVE',publication_reference,event.event_id,event.committed_at))
            self._verify_event(c,event)
        return event

    def settle_and_close(self,*,request_id,settlement_reference,sale_id,settled_minor):
        amount=int(settled_minor)
        if not all(str(x).strip() for x in (request_id,settlement_reference,sale_id)) or amount<0: raise ValueError('Settlement evidence is incomplete')
        event=self._new_event('ORDER_CLOSE',request_id,{'settlement_reference':settlement_reference,'sale_id':sale_id,'settled_minor':amount})
        with self.database.transaction() as c:
            sale=c.execute("SELECT * FROM sales WHERE sale_id=? AND state='COMPLETED'",(sale_id,)).fetchone()
            if sale is None: raise ValueError('Completed sale authority required')
            expected=int(sale['revenue_minor'])-int(sale['marketplace_fees_minor'])-int(sale['shipping_minor'])-int(sale['packaging_minor'])
            if amount!=expected: raise ValueError('Settlement does not match authoritative net proceeds')
            self._append_event_and_audit(c,event,'settle_and_close')
            c.execute('INSERT INTO settlements VALUES (?,?,?,?,?)',(settlement_reference,sale_id,amount,event.event_id,event.committed_at))
            c.execute('INSERT INTO order_closures VALUES (?,?,?,?)',(sale_id,settlement_reference,event.event_id,event.committed_at))
            self._verify_event(c,event)
        return event

    def detect_variance(self,*,request_id,exception_id,asset_id,expected_quantity):
        with self.database.connect() as c:
            row=c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=?',(asset_id,)).fetchone()
        if row is None: raise ValueError('Authoritative asset quantity not found')
        actual=int(row['quantity']); expected=int(expected_quantity)
        variance=actual-expected
        if variance==0: raise ValueError('No variance means no exception authority')
        evidence=f'expected_quantity={expected}; authoritative_quantity={actual}; variance={variance}'
        return self.services.exception.record(request_id=request_id,exception_id=exception_id,exception_type='AUTHORITATIVE_VARIANCE',evidence=evidence,source_event_id=None)

    def resolve_exception(self,*,request_id,resolution_event_id,exception_id,evidence):
        if not all(str(x).strip() for x in (request_id,resolution_event_id,exception_id,evidence)): raise ValueError('Explicit resolution request and evidence are required')
        event=self._new_event('EXCEPTION_RESOLUTION',request_id,{'resolution_event_id':resolution_event_id,'exception_id':exception_id,'evidence':evidence})
        with self.database.transaction() as c:
            ex=c.execute("SELECT * FROM exception_authority WHERE exception_id=? AND state='REVIEW'",(exception_id,)).fetchone()
            if ex is None: raise ValueError('Unresolved exception authority required')
            self._append_event_and_audit(c,event,'resolve_exception')
            c.execute('INSERT INTO exception_resolutions VALUES (?,?,?,?,?,?)',(resolution_event_id,exception_id,request_id,evidence,event.event_id,event.committed_at))
            c.execute("UPDATE exception_authority SET state='COMPLETED' WHERE exception_id=?",(exception_id,))
            c.execute('INSERT INTO exception_history(exception_id,event_id,source_event_id,exception_type,evidence,state,recorded_at) VALUES (?,?,?,?,?,?,?)',(exception_id,event.event_id,ex['source_event_id'],ex['exception_type'],evidence,'COMPLETED',event.committed_at))
            c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,'EXCEPTION_RESOLUTION',resolution_event_id,'VERIFIED',event.committed_at))
            self._verify_event(c,event)
        return event
