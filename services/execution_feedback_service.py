from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from services.base_service import AuthoritativeService

class ExecutionFeedbackBlocked(RuntimeError):
    pass

class ExecutionFeedbackService(AuthoritativeService):
    service_name = 'execution_feedback_service'

    def __init__(self, path):
        self.path = Path(path)
        self.database = DatabaseManager(self.path)
        self.database.initialize()
        self.events = EventRepository()
        super().__init__(self.database, self.events)
        with self.database.transaction() as c:
            c.executescript('''
            CREATE TABLE IF NOT EXISTS execution_feedback(
              feedback_id TEXT PRIMARY KEY,
              operating_state_id TEXT NOT NULL UNIQUE,
              feedback_request_id TEXT NOT NULL UNIQUE,
              feedback_event_id TEXT NOT NULL UNIQUE,
              feedback_code TEXT NOT NULL,
              feedback_reason TEXT NOT NULL,
              feedback_result TEXT NOT NULL CHECK(feedback_result='FEEDBACK_READY'),
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS execution_feedback_history(
              history_id INTEGER PRIMARY KEY AUTOINCREMENT,
              feedback_id TEXT NOT NULL,
              operating_state_id TEXT NOT NULL,
              feedback_event_id TEXT NOT NULL,
              feedback_code TEXT NOT NULL,
              feedback_result TEXT NOT NULL CHECK(feedback_result='FEEDBACK_READY'),
              recorded_at TEXT NOT NULL,
              UNIQUE(feedback_event_id, feedback_result)
            );
            CREATE TRIGGER IF NOT EXISTS execution_feedback_no_update BEFORE UPDATE ON execution_feedback BEGIN SELECT RAISE(ABORT,'execution_feedback is append-only'); END;
            CREATE TRIGGER IF NOT EXISTS execution_feedback_no_delete BEFORE DELETE ON execution_feedback BEGIN SELECT RAISE(ABORT,'execution_feedback is append-only'); END;
            CREATE TRIGGER IF NOT EXISTS execution_feedback_history_no_update BEFORE UPDATE ON execution_feedback_history BEGIN SELECT RAISE(ABORT,'execution_feedback_history is append-only'); END;
            CREATE TRIGGER IF NOT EXISTS execution_feedback_history_no_delete BEFORE DELETE ON execution_feedback_history BEGIN SELECT RAISE(ABORT,'execution_feedback_history is append-only'); END;
            ''')

    def reconstruct(self, *, feedback_id, operating_state_id, request_id, intent):
        if not all(str(v).strip() for v in (feedback_id, operating_state_id, request_id)) or str(intent).upper() != 'RECONSTRUCT_EXECUTION_FEEDBACK':
            raise ExecutionFeedbackBlocked('Explicit complete execution feedback authority required')
        payload = {'feedback_id': feedback_id, 'operating_state_id': operating_state_id}
        event = self._new_event('EXECUTION_FEEDBACK', request_id, payload)
        with self.database.read_connection() as c:
            prior = c.execute('SELECT * FROM event_identity WHERE request_id=?', (request_id,)).fetchone()
            if prior:
                row = c.execute('SELECT * FROM execution_feedback WHERE feedback_request_id=?', (request_id,)).fetchone()
                if row and row['feedback_id'] == feedback_id and prior['payload_sha256'] == event.payload_sha256:
                    self._replay(prior)
                    return self.get(feedback_id)
                raise ExecutionFeedbackBlocked('Execution feedback request identity mismatch')
        with self.database.transaction() as c:
            parent = c.execute("SELECT * FROM business_operating_states WHERE operating_state_id=? AND operating_state_result='OPERATING_READY'", (operating_state_id,)).fetchone()
            if not parent:
                raise ExecutionFeedbackBlocked('Accepted OPERATING_READY authority required')
            if c.execute('SELECT 1 FROM execution_feedback WHERE operating_state_id=?', (operating_state_id,)).fetchone():
                raise ExecutionFeedbackBlocked('Second execution feedback authority blocked')
            code = 'MEASURE_CONTROLLED_GROWTH_EXECUTION'
            reason = 'Capture execution feedback from the accepted controlled-growth operating state'
            preserved = ('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_ledger_postings','business_ledger_balances','business_performance_summaries','business_performance_intelligence','business_decisions','action_plans','business_priorities','execution_queues','operating_commands','business_operating_states')
            before = tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in preserved)
            self._append_event_and_audit(c, event, 'reconstruct_execution_feedback')
            c.execute('INSERT INTO execution_feedback VALUES (?,?,?,?,?,?,?,?)', (feedback_id, operating_state_id, request_id, event.event_id, code, reason, 'FEEDBACK_READY', event.committed_at))
            c.execute('INSERT INTO execution_feedback_history(feedback_id,operating_state_id,feedback_event_id,feedback_code,feedback_result,recorded_at) VALUES (?,?,?,?,?,?)', (feedback_id, operating_state_id, event.event_id, code, 'FEEDBACK_READY', event.committed_at))
            c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)', (event.event_id, 'EXECUTION_FEEDBACK', feedback_id, 'VERIFIED', event.committed_at))
            self._verify_event(c, event)
            after = tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in preserved)
            if before != after:
                raise RuntimeError('Execution feedback mutated preserved authority')
        return self.get(feedback_id)

    def _replay(self, prior):
        with self.database.transaction() as c:
            c.execute("INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES (?,?,?,?, 'BLOCKED',?)", (prior['request_id'], prior['event_id'], 'EXECUTION_FEEDBACK', prior['payload_sha256'], prior['committed_at']))

    def get(self, feedback_id):
        with self.database.read_connection() as c:
            row = c.execute('SELECT * FROM execution_feedback WHERE feedback_id=?', (feedback_id,)).fetchone()
            history = c.execute('SELECT COUNT(*) n FROM execution_feedback_history WHERE feedback_id=?', (feedback_id,)).fetchone()['n']
            if not row or history != 1:
                raise ExecutionFeedbackBlocked('Execution feedback reconstruction failed')
            return dict(row)
