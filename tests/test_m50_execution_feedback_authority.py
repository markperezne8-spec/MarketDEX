import sqlite3
import pytest
from services.m45_m49_acceptance_service import M45M49AcceptanceService
from services.execution_feedback_service import ExecutionFeedbackService, ExecutionFeedbackBlocked

FEEDBACK_ID='FEEDBACK-M50A-001'
STATE_ID='OPERATING-STATE-M49A-001'
REQUEST_ID='M50A-FEEDBACK-REQUEST-001'

def fixture(path):
    assert M45M49AcceptanceService(path).execute()['passed'] == 21
    return ExecutionFeedbackService(path)

def kwargs():
    return dict(feedback_id=FEEDBACK_ID, operating_state_id=STATE_ID, request_id=REQUEST_ID, intent='RECONSTRUCT_EXECUTION_FEEDBACK')

def test_m50_feedback_ready_exactly_once_replay_restart(tmp_path):
    path=tmp_path/'m50.sqlite3'; svc=fixture(path)
    a=svc.reconstruct(**kwargs()); b=svc.reconstruct(**kwargs()); svc=ExecutionFeedbackService(path); c=svc.reconstruct(**kwargs())
    assert a==b==c
    assert a['feedback_result']=='FEEDBACK_READY'
    assert a['feedback_code']=='MEASURE_CONTROLLED_GROWTH_EXECUTION'
    with svc.database.read_connection() as db:
        assert db.execute('SELECT COUNT(*) n FROM execution_feedback').fetchone()['n']==1
        assert db.execute('SELECT COUNT(*) n FROM execution_feedback_history').fetchone()['n']==1
        assert db.execute("SELECT COUNT(*) n FROM replay_defense_history WHERE request_id=? AND attempted_event_type='EXECUTION_FEEDBACK'",(REQUEST_ID,)).fetchone()['n']==1

def test_m50_requires_operating_ready_and_blocks_second_authority(tmp_path):
    svc=fixture(tmp_path/'blocked.sqlite3')
    bad=kwargs(); bad['operating_state_id']='UNKNOWN'
    with pytest.raises(ExecutionFeedbackBlocked): svc.reconstruct(**bad)
    svc.reconstruct(**kwargs())
    second=dict(feedback_id='SECOND',operating_state_id=STATE_ID,request_id='SECOND-REQUEST',intent='RECONSTRUCT_EXECUTION_FEEDBACK')
    with pytest.raises(ExecutionFeedbackBlocked): svc.reconstruct(**second)

def test_m50_history_is_append_only(tmp_path):
    svc=fixture(tmp_path/'append.sqlite3'); svc.reconstruct(**kwargs())
    with pytest.raises(sqlite3.IntegrityError):
        with svc.database.transaction() as c: c.execute('DELETE FROM execution_feedback_history')

def test_m50_zero_upstream_authority_mutation(tmp_path):
    svc=fixture(tmp_path/'preserve.sqlite3')
    tables=('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_ledger_postings','business_ledger_balances','business_performance_summaries','business_performance_intelligence','business_decisions','action_plans','business_priorities','execution_queues','operating_commands','business_operating_states')
    with svc.database.read_connection() as c: before=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables)
    svc.reconstruct(**kwargs())
    with svc.database.read_connection() as c: after=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables)
    assert before==after
