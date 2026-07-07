from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from services.base_service import AuthoritativeService

class BusinessDecisionBlocked(RuntimeError): pass

class BusinessDecisionService(AuthoritativeService):
    service_name='business_decision_service'
    def __init__(self,path):
        self.path=Path(path); self.database=DatabaseManager(self.path); self.database.initialize(); self.events=EventRepository(); super().__init__(self.database,self.events)
        with self.database.transaction() as c:
            c.executescript('''CREATE TABLE IF NOT EXISTS business_decisions(decision_id TEXT PRIMARY KEY,intelligence_id TEXT NOT NULL UNIQUE,decision_request_id TEXT NOT NULL UNIQUE,decision_event_id TEXT NOT NULL UNIQUE,decision_code TEXT NOT NULL,decision_reason TEXT NOT NULL,decision_result TEXT NOT NULL CHECK(decision_result='DECISION_READY'),created_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS business_decision_history(history_id INTEGER PRIMARY KEY AUTOINCREMENT,decision_id TEXT NOT NULL,intelligence_id TEXT NOT NULL,decision_event_id TEXT NOT NULL,decision_code TEXT NOT NULL,decision_result TEXT NOT NULL CHECK(decision_result='DECISION_READY'),recorded_at TEXT NOT NULL,UNIQUE(decision_event_id,decision_result)); CREATE TRIGGER IF NOT EXISTS business_decisions_no_update BEFORE UPDATE ON business_decisions BEGIN SELECT RAISE(ABORT,'business_decisions is append-only'); END; CREATE TRIGGER IF NOT EXISTS business_decisions_no_delete BEFORE DELETE ON business_decisions BEGIN SELECT RAISE(ABORT,'business_decisions is append-only'); END; CREATE TRIGGER IF NOT EXISTS business_decision_history_no_update BEFORE UPDATE ON business_decision_history BEGIN SELECT RAISE(ABORT,'business_decision_history is append-only'); END; CREATE TRIGGER IF NOT EXISTS business_decision_history_no_delete BEFORE DELETE ON business_decision_history BEGIN SELECT RAISE(ABORT,'business_decision_history is append-only'); END;''')
    def reconstruct(self,*,decision_id,intelligence_id,decision_request_id,intent):
        if not all(str(v).strip() for v in (decision_id,intelligence_id,decision_request_id)) or str(intent).upper()!='RECONSTRUCT_DECISION': raise BusinessDecisionBlocked('Explicit complete business decision authority required')
        payload={'decision_id':decision_id,'intelligence_id':intelligence_id}; event=self._new_event('BUSINESS_DECISION',decision_request_id,payload)
        with self.database.read_connection() as c:
            prior=c.execute('SELECT * FROM event_identity WHERE request_id=?',(decision_request_id,)).fetchone()
            if prior:
                row=c.execute('SELECT * FROM business_decisions WHERE decision_request_id=?',(decision_request_id,)).fetchone()
                if row and row['decision_id']==decision_id and prior['payload_sha256']==event.payload_sha256: self._replay(prior); return self.get(decision_id)
                raise BusinessDecisionBlocked('Decision request identity mismatch')
        with self.database.transaction() as c:
            intelligence=c.execute("SELECT * FROM business_performance_intelligence WHERE intelligence_id=? AND intelligence_result='INTELLIGENCE_READY'",(intelligence_id,)).fetchone()
            if not intelligence: raise BusinessDecisionBlocked('Accepted INTELLIGENCE_READY authority required')
            if c.execute('SELECT 1 FROM business_decisions WHERE intelligence_id=?',(intelligence_id,)).fetchone(): raise BusinessDecisionBlocked('Second business decision authority blocked')
            status=intelligence['performance_status']; margin=int(intelligence['profit_margin_bps']); avg_profit=int(intelligence['average_realized_profit_minor'])
            if status=='PROFITABLE' and margin>=5000 and avg_profit>0: code='SCALE_PROFITABLE_CHANNEL'; reason='PROFITABLE intelligence with margin >= 50.00% and positive average realized profit'
            elif status=='PROFITABLE' and avg_profit>0: code='MAINTAIN_AND_OPTIMIZE'; reason='PROFITABLE intelligence with positive average realized profit below scale margin threshold'
            elif status=='BREAK_EVEN': code='PROTECT_MARGIN'; reason='BREAK_EVEN intelligence requires margin protection'
            else: code='REDUCE_EXPOSURE'; reason='LOSS intelligence requires exposure reduction'
            tables=('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_ledger_postings','business_ledger_balances','business_performance_summaries','business_performance_intelligence'); counts=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables); sold=c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n']
            self._append_event_and_audit(c,event,'reconstruct_business_decision'); c.execute('INSERT INTO business_decisions VALUES (?,?,?,?,?,?,?,?)',(decision_id,intelligence_id,decision_request_id,event.event_id,code,reason,'DECISION_READY',event.committed_at)); c.execute('INSERT INTO business_decision_history(decision_id,intelligence_id,decision_event_id,decision_code,decision_result,recorded_at) VALUES (?,?,?,?,?,?)',(decision_id,intelligence_id,event.event_id,code,'DECISION_READY',event.committed_at)); c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,'BUSINESS_DECISION',decision_id,'VERIFIED',event.committed_at)); self._verify_event(c,event)
            after=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables)
            if counts!=after or sold!=c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n']: raise RuntimeError('Business decision mutated preserved authority')
        return self.get(decision_id)
    def _replay(self,prior):
        with self.database.transaction() as c: c.execute("INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES (?,?,?,?, 'BLOCKED',?)",(prior['request_id'],prior['event_id'],'BUSINESS_DECISION',prior['payload_sha256'],prior['committed_at']))
    def get(self,decision_id):
        with self.database.read_connection() as c:
            row=c.execute('SELECT * FROM business_decisions WHERE decision_id=?',(decision_id,)).fetchone(); h=c.execute('SELECT COUNT(*) n FROM business_decision_history WHERE decision_id=?',(decision_id,)).fetchone()['n']
            if not row or h!=1: raise BusinessDecisionBlocked('Business decision reconstruction failed')
            return dict(row)
