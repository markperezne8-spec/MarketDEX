from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from services.base_service import AuthoritativeService

class BusinessLedgerBalanceBlocked(RuntimeError): pass

class BusinessLedgerBalanceService(AuthoritativeService):
    service_name='business_ledger_balance_service'
    def __init__(self,path):
        self.path=Path(path); self.database=DatabaseManager(self.path); self.database.initialize(); self.events=EventRepository(); super().__init__(self.database,self.events)
        with self.database.transaction() as c:
            c.executescript('''CREATE TABLE IF NOT EXISTS business_ledger_balances(balance_id TEXT PRIMARY KEY,posting_id TEXT NOT NULL UNIQUE,balance_request_id TEXT NOT NULL UNIQUE,balance_event_id TEXT NOT NULL UNIQUE,ledger_account TEXT NOT NULL,posting_count INTEGER NOT NULL,balanced_revenue_minor INTEGER NOT NULL,balanced_cogs_minor INTEGER NOT NULL,balanced_profit_minor INTEGER NOT NULL,balance_result TEXT NOT NULL CHECK(balance_result='BALANCED'),created_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS business_ledger_balance_history(history_id INTEGER PRIMARY KEY AUTOINCREMENT,balance_id TEXT NOT NULL,posting_id TEXT NOT NULL,balance_event_id TEXT NOT NULL,ledger_account TEXT NOT NULL,balanced_profit_minor INTEGER NOT NULL,balance_result TEXT NOT NULL CHECK(balance_result='BALANCED'),recorded_at TEXT NOT NULL,UNIQUE(balance_event_id,balance_result)); CREATE TRIGGER IF NOT EXISTS business_ledger_balances_no_update BEFORE UPDATE ON business_ledger_balances BEGIN SELECT RAISE(ABORT,'business_ledger_balances is append-only'); END; CREATE TRIGGER IF NOT EXISTS business_ledger_balances_no_delete BEFORE DELETE ON business_ledger_balances BEGIN SELECT RAISE(ABORT,'business_ledger_balances is append-only'); END; CREATE TRIGGER IF NOT EXISTS business_ledger_balance_history_no_update BEFORE UPDATE ON business_ledger_balance_history BEGIN SELECT RAISE(ABORT,'business_ledger_balance_history is append-only'); END; CREATE TRIGGER IF NOT EXISTS business_ledger_balance_history_no_delete BEFORE DELETE ON business_ledger_balance_history BEGIN SELECT RAISE(ABORT,'business_ledger_balance_history is append-only'); END;''')
    def balance(self,*,balance_id,posting_id,balance_request_id,ledger_account,intent):
        if not all(str(v).strip() for v in (balance_id,posting_id,balance_request_id,ledger_account)) or str(intent).upper()!='BALANCE': raise BusinessLedgerBalanceBlocked('Explicit complete ledger balance authority required')
        payload={'balance_id':balance_id,'posting_id':posting_id,'ledger_account':ledger_account}; event=self._new_event('BUSINESS_LEDGER_BALANCE',balance_request_id,payload)
        with self.database.read_connection() as c:
            prior=c.execute('SELECT * FROM event_identity WHERE request_id=?',(balance_request_id,)).fetchone()
            if prior:
                row=c.execute('SELECT * FROM business_ledger_balances WHERE balance_request_id=?',(balance_request_id,)).fetchone()
                if row and row['balance_id']==balance_id and prior['payload_sha256']==event.payload_sha256: self._replay(prior); return self.get(balance_id)
                raise BusinessLedgerBalanceBlocked('Balance request identity mismatch')
        with self.database.transaction() as c:
            posting=c.execute("SELECT * FROM business_ledger_postings WHERE posting_id=? AND ledger_account=? AND posting_result='POSTED'",(posting_id,ledger_account)).fetchone()
            if not posting: raise BusinessLedgerBalanceBlocked('Accepted POSTED ledger authority required')
            if c.execute('SELECT 1 FROM business_ledger_balances WHERE posting_id=?',(posting_id,)).fetchone(): raise BusinessLedgerBalanceBlocked('Second ledger balance blocked')
            aggregate=c.execute("SELECT COUNT(*) posting_count,COALESCE(SUM(posted_revenue_minor),0) revenue,COALESCE(SUM(posted_cogs_minor),0) cogs,COALESCE(SUM(posted_profit_minor),0) profit FROM business_ledger_postings WHERE ledger_account=? AND posting_result='POSTED'",(ledger_account,)).fetchone()
            account_profit=c.execute("SELECT COALESCE(SUM(posted_profit_minor),0) profit FROM business_ledger_postings WHERE ledger_account=? AND posting_result='POSTED'",(ledger_account,)).fetchone()['profit']
            if int(aggregate['profit'])!=int(account_profit) or int(aggregate['posting_count'])<1: raise BusinessLedgerBalanceBlocked('Ledger posted-profit aggregate mismatch')
            tables=('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_ledger_postings'); counts=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables); sold=c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n']
            self._append_event_and_audit(c,event,'reconstruct_business_ledger_balance'); c.execute('INSERT INTO business_ledger_balances VALUES (?,?,?,?,?,?,?,?,?,?,?)',(balance_id,posting_id,balance_request_id,event.event_id,ledger_account,int(aggregate['posting_count']),int(aggregate['revenue']),int(aggregate['cogs']),int(aggregate['profit']),'BALANCED',event.committed_at)); c.execute('INSERT INTO business_ledger_balance_history(balance_id,posting_id,balance_event_id,ledger_account,balanced_profit_minor,balance_result,recorded_at) VALUES (?,?,?,?,?,?,?)',(balance_id,posting_id,event.event_id,ledger_account,int(aggregate['profit']),'BALANCED',event.committed_at)); c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,'BUSINESS_LEDGER_BALANCE',balance_id,'VERIFIED',event.committed_at)); self._verify_event(c,event)
            after=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables)
            if counts!=after or sold!=c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n']: raise RuntimeError('Ledger balance mutated preserved authority')
        return self.get(balance_id)
    def _replay(self,prior):
        with self.database.transaction() as c: c.execute("INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES (?,?,?,?, 'BLOCKED',?)",(prior['request_id'],prior['event_id'],'BUSINESS_LEDGER_BALANCE',prior['payload_sha256'],prior['committed_at']))
    def get(self,balance_id):
        with self.database.read_connection() as c:
            row=c.execute('SELECT * FROM business_ledger_balances WHERE balance_id=?',(balance_id,)).fetchone(); h=c.execute('SELECT COUNT(*) n FROM business_ledger_balance_history WHERE balance_id=?',(balance_id,)).fetchone()['n']
            if not row or h!=1: raise BusinessLedgerBalanceBlocked('Ledger balance reconstruction failed')
            return dict(row)
