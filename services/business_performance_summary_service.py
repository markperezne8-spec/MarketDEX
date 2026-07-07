from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from services.base_service import AuthoritativeService

class BusinessPerformanceSummaryBlocked(RuntimeError): pass

class BusinessPerformanceSummaryService(AuthoritativeService):
    service_name='business_performance_summary_service'
    def __init__(self,path):
        self.path=Path(path); self.database=DatabaseManager(self.path); self.database.initialize(); self.events=EventRepository(); super().__init__(self.database,self.events)
        with self.database.transaction() as c:
            c.executescript('''CREATE TABLE IF NOT EXISTS business_performance_summaries(summary_id TEXT PRIMARY KEY,balance_id TEXT NOT NULL UNIQUE,summary_request_id TEXT NOT NULL UNIQUE,summary_event_id TEXT NOT NULL UNIQUE,ledger_account TEXT NOT NULL,sale_count INTEGER NOT NULL,revenue_minor INTEGER NOT NULL,cogs_minor INTEGER NOT NULL,realized_profit_minor INTEGER NOT NULL,summary_result TEXT NOT NULL CHECK(summary_result='SUMMARIZED'),created_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS business_performance_summary_history(history_id INTEGER PRIMARY KEY AUTOINCREMENT,summary_id TEXT NOT NULL,balance_id TEXT NOT NULL,summary_event_id TEXT NOT NULL,realized_profit_minor INTEGER NOT NULL,summary_result TEXT NOT NULL CHECK(summary_result='SUMMARIZED'),recorded_at TEXT NOT NULL,UNIQUE(summary_event_id,summary_result)); CREATE TRIGGER IF NOT EXISTS business_performance_summaries_no_update BEFORE UPDATE ON business_performance_summaries BEGIN SELECT RAISE(ABORT,'business_performance_summaries is append-only'); END; CREATE TRIGGER IF NOT EXISTS business_performance_summaries_no_delete BEFORE DELETE ON business_performance_summaries BEGIN SELECT RAISE(ABORT,'business_performance_summaries is append-only'); END; CREATE TRIGGER IF NOT EXISTS business_performance_summary_history_no_update BEFORE UPDATE ON business_performance_summary_history BEGIN SELECT RAISE(ABORT,'business_performance_summary_history is append-only'); END; CREATE TRIGGER IF NOT EXISTS business_performance_summary_history_no_delete BEFORE DELETE ON business_performance_summary_history BEGIN SELECT RAISE(ABORT,'business_performance_summary_history is append-only'); END;''')
    def summarize(self,*,summary_id,balance_id,summary_request_id,intent):
        if not all(str(v).strip() for v in (summary_id,balance_id,summary_request_id)) or str(intent).upper()!='SUMMARIZE': raise BusinessPerformanceSummaryBlocked('Explicit complete business performance summary authority required')
        payload={'summary_id':summary_id,'balance_id':balance_id}; event=self._new_event('BUSINESS_PERFORMANCE_SUMMARY',summary_request_id,payload)
        with self.database.read_connection() as c:
            prior=c.execute('SELECT * FROM event_identity WHERE request_id=?',(summary_request_id,)).fetchone()
            if prior:
                row=c.execute('SELECT * FROM business_performance_summaries WHERE summary_request_id=?',(summary_request_id,)).fetchone()
                if row and row['summary_id']==summary_id and prior['payload_sha256']==event.payload_sha256: self._replay(prior); return self.get(summary_id)
                raise BusinessPerformanceSummaryBlocked('Summary request identity mismatch')
        with self.database.transaction() as c:
            balance=c.execute("SELECT * FROM business_ledger_balances WHERE balance_id=? AND balance_result='BALANCED'",(balance_id,)).fetchone()
            if not balance: raise BusinessPerformanceSummaryBlocked('Accepted BALANCED authority required')
            if c.execute('SELECT 1 FROM business_performance_summaries WHERE balance_id=?',(balance_id,)).fetchone(): raise BusinessPerformanceSummaryBlocked('Second business performance summary blocked')
            aggregate=c.execute("SELECT COUNT(DISTINCT sale_id) sale_count,COALESCE(SUM(posted_revenue_minor),0) revenue,COALESCE(SUM(posted_cogs_minor),0) cogs,COALESCE(SUM(posted_profit_minor),0) profit FROM business_ledger_postings WHERE ledger_account=? AND posting_result='POSTED'",(balance['ledger_account'],)).fetchone()
            if int(aggregate['profit'])!=int(balance['balanced_profit_minor']) or int(aggregate['revenue'])!=int(balance['balanced_revenue_minor']) or int(aggregate['cogs'])!=int(balance['balanced_cogs_minor']): raise BusinessPerformanceSummaryBlocked('Balanced ledger truth mismatch')
            tables=('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_ledger_postings','business_ledger_balances'); counts=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables); sold=c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n']
            self._append_event_and_audit(c,event,'reconstruct_business_performance_summary'); c.execute('INSERT INTO business_performance_summaries VALUES (?,?,?,?,?,?,?,?,?,?,?)',(summary_id,balance_id,summary_request_id,event.event_id,balance['ledger_account'],int(aggregate['sale_count']),int(aggregate['revenue']),int(aggregate['cogs']),int(aggregate['profit']),'SUMMARIZED',event.committed_at)); c.execute('INSERT INTO business_performance_summary_history(summary_id,balance_id,summary_event_id,realized_profit_minor,summary_result,recorded_at) VALUES (?,?,?,?,?,?)',(summary_id,balance_id,event.event_id,int(aggregate['profit']),'SUMMARIZED',event.committed_at)); c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,'BUSINESS_PERFORMANCE_SUMMARY',summary_id,'VERIFIED',event.committed_at)); self._verify_event(c,event)
            after=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables)
            if counts!=after or sold!=c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n']: raise RuntimeError('Performance summary mutated preserved authority')
        return self.get(summary_id)
    def _replay(self,prior):
        with self.database.transaction() as c: c.execute("INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES (?,?,?,?, 'BLOCKED',?)",(prior['request_id'],prior['event_id'],'BUSINESS_PERFORMANCE_SUMMARY',prior['payload_sha256'],prior['committed_at']))
    def get(self,summary_id):
        with self.database.read_connection() as c:
            row=c.execute('SELECT * FROM business_performance_summaries WHERE summary_id=?',(summary_id,)).fetchone(); h=c.execute('SELECT COUNT(*) n FROM business_performance_summary_history WHERE summary_id=?',(summary_id,)).fetchone()['n']
            if not row or h!=1: raise BusinessPerformanceSummaryBlocked('Business performance summary reconstruction failed')
            return dict(row)
