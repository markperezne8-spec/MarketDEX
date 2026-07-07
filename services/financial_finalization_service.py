from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from repositories.financial_finalization_repository import FinancialFinalizationRepository
from services.base_service import AuthoritativeService

class FinancialFinalizationBlocked(RuntimeError): pass

class FinancialFinalizationService(AuthoritativeService):
    service_name='financial_finalization_service'
    def __init__(self,path):
        self.path=Path(path); self.database=DatabaseManager(self.path); self.database.initialize(); self.events=EventRepository(); self.repository=FinancialFinalizationRepository(); super().__init__(self.database,self.events)
        with self.database.transaction() as c: self.repository.ensure_schema(c)

    def finalize(self,*,finalization_id,closure_id,sale_id,settlement_id,finalization_request_id,intent):
        if not all(str(v).strip() for v in (finalization_id,closure_id,sale_id,settlement_id,finalization_request_id)) or str(intent).upper()!='FINALIZE': raise FinancialFinalizationBlocked('Explicit complete financial finalization authority required')
        payload={'finalization_id':finalization_id,'closure_id':closure_id,'sale_id':sale_id,'settlement_id':settlement_id}; event=self._new_event('FINANCIAL_FINALIZATION',finalization_request_id,payload)
        with self.database.read_connection() as c:
            prior=c.execute('SELECT * FROM event_identity WHERE request_id=?',(finalization_request_id,)).fetchone()
            if prior:
                row=self.repository.by_request(c,finalization_request_id)
                if row and row['finalization_id']==finalization_id and prior['payload_sha256']==event.payload_sha256:
                    self._replay(prior); return self.get(finalization_id)
                raise FinancialFinalizationBlocked('Finalization request identity mismatch')
        with self.database.transaction() as c:
            closure=c.execute("SELECT * FROM order_closures WHERE closure_id=? AND sale_id=? AND settlement_id=? AND closure_result='CLOSED'",(closure_id,sale_id,settlement_id)).fetchone(); sale=c.execute("SELECT * FROM sales WHERE sale_id=? AND state='COMPLETED'",(sale_id,)).fetchone(); financial=c.execute('SELECT * FROM sales_financial_history WHERE sale_id=? AND event_id=?',(sale_id,sale['created_event_id'] if sale else '')).fetchone(); settlement=c.execute("SELECT * FROM settlement_executions WHERE settlement_id=? AND sale_id=? AND settlement_result='SETTLED'",(settlement_id,sale_id)).fetchone()
            if not all((closure,sale,financial,settlement)): raise FinancialFinalizationBlocked('Accepted CLOSED order financial lineage required')
            if c.execute('SELECT 1 FROM financial_finalizations WHERE closure_id=? OR sale_id=? OR settlement_id=?',(closure_id,sale_id,settlement_id)).fetchone(): raise FinancialFinalizationBlocked('Second financial finalization blocked')
            expected=int(financial['revenue_minor'])-int(financial['marketplace_fees_minor'])-int(financial['shipping_minor'])-int(financial['packaging_minor'])
            if expected!=int(settlement['observed_payout_minor']): raise FinancialFinalizationBlocked('Settlement payout and M24 financial truth mismatch')
            counts=(c.execute('SELECT COUNT(*) n FROM sales').fetchone()['n'],c.execute('SELECT COUNT(*) n FROM sales_financial_history').fetchone()['n'],c.execute('SELECT COUNT(*) n FROM settlement_executions').fetchone()['n'],c.execute('SELECT COUNT(*) n FROM order_closures').fetchone()['n'],c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n']); inv=c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=?',(sale['asset_id'],)).fetchone()['quantity']
            self._append_event_and_audit(c,event,'finalize_closed_order_financials'); self.repository.append(c,finalization_id=finalization_id,closure_id=closure_id,sale_id=sale_id,settlement_id=settlement_id,request_id=finalization_request_id,event_id=event.event_id,financial=financial,observed_payout_minor=settlement['observed_payout_minor'],created_at=event.committed_at); c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,'FINANCIAL_FINALIZATION',finalization_id,'VERIFIED',event.committed_at)); self._verify_event(c,event)
            after=(c.execute('SELECT COUNT(*) n FROM sales').fetchone()['n'],c.execute('SELECT COUNT(*) n FROM sales_financial_history').fetchone()['n'],c.execute('SELECT COUNT(*) n FROM settlement_executions').fetchone()['n'],c.execute('SELECT COUNT(*) n FROM order_closures').fetchone()['n'],c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n'])
            if counts!=after or c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=?',(sale['asset_id'],)).fetchone()['quantity']!=inv: raise RuntimeError('Finalization mutated preserved authority')
        return self.get(finalization_id)

    def _replay(self,prior):
        with self.database.transaction() as c: c.execute("INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES (?,?,?,?, 'BLOCKED',?)",(prior['request_id'],prior['event_id'],'FINANCIAL_FINALIZATION',prior['payload_sha256'],prior['committed_at']))
    def get(self,finalization_id):
        with self.database.read_connection() as c:
            row=self.repository.by_id(c,finalization_id); history=c.execute('SELECT COUNT(*) n FROM financial_finalization_history WHERE finalization_id=?',(finalization_id,)).fetchone()['n']; audit=None if not row else c.execute("SELECT 1 FROM audit_events WHERE event_id=? AND authority_type='FINANCIAL_FINALIZATION' AND authority_id=? AND verification_result='VERIFIED'",(row['finalization_event_id'],finalization_id)).fetchone()
            if not row or history!=1 or not audit: raise FinancialFinalizationBlocked('Financial finalization reconstruction failed')
            return dict(row)
