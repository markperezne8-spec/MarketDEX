from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from services.base_service import AuthoritativeService

class ProfitRecognitionBlocked(RuntimeError): pass

class ProfitRecognitionService(AuthoritativeService):
    service_name='profit_recognition_service'
    def __init__(self,path):
        self.path=Path(path); self.database=DatabaseManager(self.path); self.database.initialize(); self.events=EventRepository(); super().__init__(self.database,self.events)
        with self.database.transaction() as c:
            c.executescript('''CREATE TABLE IF NOT EXISTS profit_recognitions(recognition_id TEXT PRIMARY KEY,finalization_id TEXT NOT NULL UNIQUE,sale_id TEXT NOT NULL UNIQUE,recognition_request_id TEXT NOT NULL UNIQUE,recognition_event_id TEXT NOT NULL UNIQUE,recognized_revenue_minor INTEGER NOT NULL,recognized_cogs_minor INTEGER NOT NULL,recognized_profit_minor INTEGER NOT NULL,recognition_result TEXT NOT NULL CHECK(recognition_result='PROFIT_RECOGNIZED'),created_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS profit_recognition_history(history_id INTEGER PRIMARY KEY AUTOINCREMENT,recognition_id TEXT NOT NULL,finalization_id TEXT NOT NULL,sale_id TEXT NOT NULL,recognition_event_id TEXT NOT NULL,recognized_profit_minor INTEGER NOT NULL,recognition_result TEXT NOT NULL CHECK(recognition_result='PROFIT_RECOGNIZED'),recorded_at TEXT NOT NULL,UNIQUE(recognition_event_id,recognition_result)); CREATE TRIGGER IF NOT EXISTS profit_recognitions_no_update BEFORE UPDATE ON profit_recognitions BEGIN SELECT RAISE(ABORT,'profit_recognitions is append-only'); END; CREATE TRIGGER IF NOT EXISTS profit_recognitions_no_delete BEFORE DELETE ON profit_recognitions BEGIN SELECT RAISE(ABORT,'profit_recognitions is append-only'); END; CREATE TRIGGER IF NOT EXISTS profit_recognition_history_no_update BEFORE UPDATE ON profit_recognition_history BEGIN SELECT RAISE(ABORT,'profit_recognition_history is append-only'); END; CREATE TRIGGER IF NOT EXISTS profit_recognition_history_no_delete BEFORE DELETE ON profit_recognition_history BEGIN SELECT RAISE(ABORT,'profit_recognition_history is append-only'); END;''')
    def recognize(self,*,recognition_id,finalization_id,sale_id,recognition_request_id,intent):
        if not all(str(v).strip() for v in (recognition_id,finalization_id,sale_id,recognition_request_id)) or str(intent).upper()!='RECOGNIZE': raise ProfitRecognitionBlocked('Explicit complete profit recognition authority required')
        payload={'recognition_id':recognition_id,'finalization_id':finalization_id,'sale_id':sale_id}; event=self._new_event('PROFIT_RECOGNITION',recognition_request_id,payload)
        with self.database.read_connection() as c:
            prior=c.execute('SELECT * FROM event_identity WHERE request_id=?',(recognition_request_id,)).fetchone()
            if prior:
                row=c.execute('SELECT * FROM profit_recognitions WHERE recognition_request_id=?',(recognition_request_id,)).fetchone()
                if row and row['recognition_id']==recognition_id and prior['payload_sha256']==event.payload_sha256: self._replay(prior); return self.get(recognition_id)
                raise ProfitRecognitionBlocked('Recognition request identity mismatch')
        with self.database.transaction() as c:
            final=c.execute("SELECT * FROM financial_finalizations WHERE finalization_id=? AND sale_id=? AND finalization_result='FINALIZED'",(finalization_id,sale_id)).fetchone(); financial=c.execute('SELECT * FROM sales_financial_history WHERE sale_id=?',(sale_id,)).fetchone()
            if not final or not financial: raise ProfitRecognitionBlocked('Accepted FINALIZED sale financial truth required')
            if c.execute('SELECT 1 FROM profit_recognitions WHERE finalization_id=? OR sale_id=?',(finalization_id,sale_id)).fetchone(): raise ProfitRecognitionBlocked('Second profit recognition blocked')
            if any(int(final[k])!=int(financial[k]) for k in ('revenue_minor','cogs_minor','profit_minor')): raise ProfitRecognitionBlocked('Finalized financial truth mismatch')
            counts=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in ('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations')); sold=c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n']; inv=c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=(SELECT asset_id FROM sales WHERE sale_id=?)',(sale_id,)).fetchone()['quantity']
            self._append_event_and_audit(c,event,'recognize_finalized_sale_profit'); c.execute('INSERT INTO profit_recognitions VALUES (?,?,?,?,?,?,?,?,?,?)',(recognition_id,finalization_id,sale_id,recognition_request_id,event.event_id,int(final['revenue_minor']),int(final['cogs_minor']),int(final['profit_minor']),'PROFIT_RECOGNIZED',event.committed_at)); c.execute('INSERT INTO profit_recognition_history(recognition_id,finalization_id,sale_id,recognition_event_id,recognized_profit_minor,recognition_result,recorded_at) VALUES (?,?,?,?,?,?,?)',(recognition_id,finalization_id,sale_id,event.event_id,int(final['profit_minor']),'PROFIT_RECOGNIZED',event.committed_at)); c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,'PROFIT_RECOGNITION',recognition_id,'VERIFIED',event.committed_at)); self._verify_event(c,event)
            after=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in ('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations'))
            if counts!=after or sold!=c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n'] or inv!=c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=(SELECT asset_id FROM sales WHERE sale_id=?)',(sale_id,)).fetchone()['quantity']: raise RuntimeError('Profit recognition mutated preserved authority')
        return self.get(recognition_id)
    def _replay(self,prior):
        with self.database.transaction() as c: c.execute("INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES (?,?,?,?, 'BLOCKED',?)",(prior['request_id'],prior['event_id'],'PROFIT_RECOGNITION',prior['payload_sha256'],prior['committed_at']))
    def get(self,recognition_id):
        with self.database.read_connection() as c:
            row=c.execute('SELECT * FROM profit_recognitions WHERE recognition_id=?',(recognition_id,)).fetchone(); h=c.execute('SELECT COUNT(*) n FROM profit_recognition_history WHERE recognition_id=?',(recognition_id,)).fetchone()['n']
            if not row or h!=1: raise ProfitRecognitionBlocked('Profit recognition reconstruction failed')
            return dict(row)
