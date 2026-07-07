from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from services.base_service import AuthoritativeService

class BusinessLedgerPostingBlocked(RuntimeError): pass

class BusinessLedgerPostingService(AuthoritativeService):
    service_name='business_ledger_posting_service'
    def __init__(self,path):
        self.path=Path(path); self.database=DatabaseManager(self.path); self.database.initialize(); self.events=EventRepository(); super().__init__(self.database,self.events)
        with self.database.transaction() as c:
            c.executescript('''CREATE TABLE IF NOT EXISTS business_ledger_postings(posting_id TEXT PRIMARY KEY,recognition_id TEXT NOT NULL UNIQUE,sale_id TEXT NOT NULL UNIQUE,posting_request_id TEXT NOT NULL UNIQUE,posting_event_id TEXT NOT NULL UNIQUE,ledger_account TEXT NOT NULL,posted_revenue_minor INTEGER NOT NULL,posted_cogs_minor INTEGER NOT NULL,posted_profit_minor INTEGER NOT NULL,posting_result TEXT NOT NULL CHECK(posting_result='POSTED'),created_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS business_ledger_history(history_id INTEGER PRIMARY KEY AUTOINCREMENT,posting_id TEXT NOT NULL,recognition_id TEXT NOT NULL,sale_id TEXT NOT NULL,posting_event_id TEXT NOT NULL,ledger_account TEXT NOT NULL,posted_profit_minor INTEGER NOT NULL,posting_result TEXT NOT NULL CHECK(posting_result='POSTED'),recorded_at TEXT NOT NULL,UNIQUE(posting_event_id,posting_result)); CREATE TRIGGER IF NOT EXISTS business_ledger_postings_no_update BEFORE UPDATE ON business_ledger_postings BEGIN SELECT RAISE(ABORT,'business_ledger_postings is append-only'); END; CREATE TRIGGER IF NOT EXISTS business_ledger_postings_no_delete BEFORE DELETE ON business_ledger_postings BEGIN SELECT RAISE(ABORT,'business_ledger_postings is append-only'); END; CREATE TRIGGER IF NOT EXISTS business_ledger_history_no_update BEFORE UPDATE ON business_ledger_history BEGIN SELECT RAISE(ABORT,'business_ledger_history is append-only'); END; CREATE TRIGGER IF NOT EXISTS business_ledger_history_no_delete BEFORE DELETE ON business_ledger_history BEGIN SELECT RAISE(ABORT,'business_ledger_history is append-only'); END;''')
    def post(self,*,posting_id,recognition_id,sale_id,posting_request_id,ledger_account,intent):
        if not all(str(v).strip() for v in (posting_id,recognition_id,sale_id,posting_request_id,ledger_account)) or str(intent).upper()!='POST': raise BusinessLedgerPostingBlocked('Explicit complete business ledger posting authority required')
        payload={'posting_id':posting_id,'recognition_id':recognition_id,'sale_id':sale_id,'ledger_account':ledger_account}; event=self._new_event('BUSINESS_LEDGER_POSTING',posting_request_id,payload)
        with self.database.read_connection() as c:
            prior=c.execute('SELECT * FROM event_identity WHERE request_id=?',(posting_request_id,)).fetchone()
            if prior:
                row=c.execute('SELECT * FROM business_ledger_postings WHERE posting_request_id=?',(posting_request_id,)).fetchone()
                if row and row['posting_id']==posting_id and prior['payload_sha256']==event.payload_sha256: self._replay(prior); return self.get(posting_id)
                raise BusinessLedgerPostingBlocked('Posting request identity mismatch')
        with self.database.transaction() as c:
            recognition=c.execute("SELECT * FROM profit_recognitions WHERE recognition_id=? AND sale_id=? AND recognition_result='PROFIT_RECOGNIZED'",(recognition_id,sale_id)).fetchone()
            if not recognition: raise BusinessLedgerPostingBlocked('Accepted PROFIT_RECOGNIZED authority required')
            if c.execute('SELECT 1 FROM business_ledger_postings WHERE recognition_id=? OR sale_id=?',(recognition_id,sale_id)).fetchone(): raise BusinessLedgerPostingBlocked('Second business ledger posting blocked')
            counts=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in ('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions')); sold=c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n']; inv=c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=(SELECT asset_id FROM sales WHERE sale_id=?)',(sale_id,)).fetchone()['quantity']
            self._append_event_and_audit(c,event,'post_recognized_profit_to_business_ledger'); c.execute('INSERT INTO business_ledger_postings VALUES (?,?,?,?,?,?,?,?,?,?,?)',(posting_id,recognition_id,sale_id,posting_request_id,event.event_id,ledger_account,int(recognition['recognized_revenue_minor']),int(recognition['recognized_cogs_minor']),int(recognition['recognized_profit_minor']),'POSTED',event.committed_at)); c.execute('INSERT INTO business_ledger_history(posting_id,recognition_id,sale_id,posting_event_id,ledger_account,posted_profit_minor,posting_result,recorded_at) VALUES (?,?,?,?,?,?,?,?)',(posting_id,recognition_id,sale_id,event.event_id,ledger_account,int(recognition['recognized_profit_minor']),'POSTED',event.committed_at)); c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,'BUSINESS_LEDGER_POSTING',posting_id,'VERIFIED',event.committed_at)); self._verify_event(c,event)
            after=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in ('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions'))
            if counts!=after or sold!=c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n'] or inv!=c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=(SELECT asset_id FROM sales WHERE sale_id=?)',(sale_id,)).fetchone()['quantity']: raise RuntimeError('Ledger posting mutated preserved authority')
        return self.get(posting_id)
    def _replay(self,prior):
        with self.database.transaction() as c: c.execute("INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES (?,?,?,?, 'BLOCKED',?)",(prior['request_id'],prior['event_id'],'BUSINESS_LEDGER_POSTING',prior['payload_sha256'],prior['committed_at']))
    def get(self,posting_id):
        with self.database.read_connection() as c:
            row=c.execute('SELECT * FROM business_ledger_postings WHERE posting_id=?',(posting_id,)).fetchone(); h=c.execute('SELECT COUNT(*) n FROM business_ledger_history WHERE posting_id=?',(posting_id,)).fetchone()['n']
            if not row or h!=1: raise BusinessLedgerPostingBlocked('Business ledger posting reconstruction failed')
            return dict(row)
