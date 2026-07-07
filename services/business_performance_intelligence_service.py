from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from services.base_service import AuthoritativeService

class BusinessPerformanceIntelligenceBlocked(RuntimeError): pass

class BusinessPerformanceIntelligenceService(AuthoritativeService):
    service_name='business_performance_intelligence_service'
    def __init__(self,path):
        self.path=Path(path); self.database=DatabaseManager(self.path); self.database.initialize(); self.events=EventRepository(); super().__init__(self.database,self.events)
        with self.database.transaction() as c:
            c.executescript('''CREATE TABLE IF NOT EXISTS business_performance_intelligence(intelligence_id TEXT PRIMARY KEY,summary_id TEXT NOT NULL UNIQUE,intelligence_request_id TEXT NOT NULL UNIQUE,intelligence_event_id TEXT NOT NULL UNIQUE,sale_count INTEGER NOT NULL,revenue_minor INTEGER NOT NULL,realized_profit_minor INTEGER NOT NULL,profit_margin_bps INTEGER NOT NULL,average_revenue_minor INTEGER NOT NULL,average_realized_profit_minor INTEGER NOT NULL,performance_status TEXT NOT NULL,intelligence_result TEXT NOT NULL CHECK(intelligence_result='INTELLIGENCE_READY'),created_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS business_performance_intelligence_history(history_id INTEGER PRIMARY KEY AUTOINCREMENT,intelligence_id TEXT NOT NULL,summary_id TEXT NOT NULL,intelligence_event_id TEXT NOT NULL,profit_margin_bps INTEGER NOT NULL,performance_status TEXT NOT NULL,intelligence_result TEXT NOT NULL CHECK(intelligence_result='INTELLIGENCE_READY'),recorded_at TEXT NOT NULL,UNIQUE(intelligence_event_id,intelligence_result)); CREATE TRIGGER IF NOT EXISTS business_performance_intelligence_no_update BEFORE UPDATE ON business_performance_intelligence BEGIN SELECT RAISE(ABORT,'business_performance_intelligence is append-only'); END; CREATE TRIGGER IF NOT EXISTS business_performance_intelligence_no_delete BEFORE DELETE ON business_performance_intelligence BEGIN SELECT RAISE(ABORT,'business_performance_intelligence is append-only'); END; CREATE TRIGGER IF NOT EXISTS business_performance_intelligence_history_no_update BEFORE UPDATE ON business_performance_intelligence_history BEGIN SELECT RAISE(ABORT,'business_performance_intelligence_history is append-only'); END; CREATE TRIGGER IF NOT EXISTS business_performance_intelligence_history_no_delete BEFORE DELETE ON business_performance_intelligence_history BEGIN SELECT RAISE(ABORT,'business_performance_intelligence_history is append-only'); END;''')
    def reconstruct(self,*,intelligence_id,summary_id,intelligence_request_id,intent):
        if not all(str(v).strip() for v in (intelligence_id,summary_id,intelligence_request_id)) or str(intent).upper()!='RECONSTRUCT_INTELLIGENCE': raise BusinessPerformanceIntelligenceBlocked('Explicit complete performance intelligence authority required')
        payload={'intelligence_id':intelligence_id,'summary_id':summary_id}; event=self._new_event('BUSINESS_PERFORMANCE_INTELLIGENCE',intelligence_request_id,payload)
        with self.database.read_connection() as c:
            prior=c.execute('SELECT * FROM event_identity WHERE request_id=?',(intelligence_request_id,)).fetchone()
            if prior:
                row=c.execute('SELECT * FROM business_performance_intelligence WHERE intelligence_request_id=?',(intelligence_request_id,)).fetchone()
                if row and row['intelligence_id']==intelligence_id and prior['payload_sha256']==event.payload_sha256: self._replay(prior); return self.get(intelligence_id)
                raise BusinessPerformanceIntelligenceBlocked('Intelligence request identity mismatch')
        with self.database.transaction() as c:
            summary=c.execute("SELECT * FROM business_performance_summaries WHERE summary_id=? AND summary_result='SUMMARIZED'",(summary_id,)).fetchone()
            if not summary: raise BusinessPerformanceIntelligenceBlocked('Accepted SUMMARIZED authority required')
            if c.execute('SELECT 1 FROM business_performance_intelligence WHERE summary_id=?',(summary_id,)).fetchone(): raise BusinessPerformanceIntelligenceBlocked('Second performance intelligence authority blocked')
            sales=int(summary['sale_count']); revenue=int(summary['revenue_minor']); profit=int(summary['realized_profit_minor'])
            if sales<=0 or revenue<=0: raise BusinessPerformanceIntelligenceBlocked('Positive summarized sale and revenue authority required')
            margin=(profit*10000)//revenue; avg_revenue=revenue//sales; avg_profit=profit//sales; status='PROFITABLE' if profit>0 else ('BREAK_EVEN' if profit==0 else 'LOSS')
            tables=('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_ledger_postings','business_ledger_balances','business_performance_summaries'); counts=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables); sold=c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n']
            self._append_event_and_audit(c,event,'reconstruct_business_performance_intelligence'); c.execute('INSERT INTO business_performance_intelligence VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',(intelligence_id,summary_id,intelligence_request_id,event.event_id,sales,revenue,profit,margin,avg_revenue,avg_profit,status,'INTELLIGENCE_READY',event.committed_at)); c.execute('INSERT INTO business_performance_intelligence_history(intelligence_id,summary_id,intelligence_event_id,profit_margin_bps,performance_status,intelligence_result,recorded_at) VALUES (?,?,?,?,?,?,?)',(intelligence_id,summary_id,event.event_id,margin,status,'INTELLIGENCE_READY',event.committed_at)); c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,'BUSINESS_PERFORMANCE_INTELLIGENCE',intelligence_id,'VERIFIED',event.committed_at)); self._verify_event(c,event)
            after=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables)
            if counts!=after or sold!=c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n']: raise RuntimeError('Performance intelligence mutated preserved authority')
        return self.get(intelligence_id)
    def _replay(self,prior):
        with self.database.transaction() as c: c.execute("INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES (?,?,?,?, 'BLOCKED',?)",(prior['request_id'],prior['event_id'],'BUSINESS_PERFORMANCE_INTELLIGENCE',prior['payload_sha256'],prior['committed_at']))
    def get(self,intelligence_id):
        with self.database.read_connection() as c:
            row=c.execute('SELECT * FROM business_performance_intelligence WHERE intelligence_id=?',(intelligence_id,)).fetchone(); h=c.execute('SELECT COUNT(*) n FROM business_performance_intelligence_history WHERE intelligence_id=?',(intelligence_id,)).fetchone()['n']
            if not row or h!=1: raise BusinessPerformanceIntelligenceBlocked('Performance intelligence reconstruction failed')
            return dict(row)
