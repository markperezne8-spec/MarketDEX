import sqlite3
import pytest
from services.m45_m49_acceptance_service import M45M49AcceptanceService
from services.execution_feedback_service import ExecutionFeedbackService
from services.adaptive_feedback_chain_service import AdaptiveFeedbackChainService, AdaptiveFeedbackBlocked

CHAIN=(('EXECUTION_OUTCOME','OUTCOME-M51-001','FEEDBACK-M50A-001','M51-REQUEST-001','OUTCOME_READY'),('VARIANCE_INTELLIGENCE','VARIANCE-M52-001','OUTCOME-M51-001','M52-REQUEST-001','VARIANCE_READY'),('OPERATING_ADJUSTMENT','ADJUSTMENT-M53-001','VARIANCE-M52-001','M53-REQUEST-001','ADJUSTMENT_READY'),('ADAPTIVE_COMMAND','ADAPTIVE-COMMAND-M54-001','ADJUSTMENT-M53-001','M54-REQUEST-001','ADAPTIVE_COMMAND_READY'),('ADAPTIVE_OPERATING_STATE','ADAPTIVE-STATE-M55-001','ADAPTIVE-COMMAND-M54-001','M55-REQUEST-001','ADAPTIVE_OPERATING_READY'))

def fixture(path):
 assert M45M49AcceptanceService(path).execute()['passed']==21
 ExecutionFeedbackService(path).reconstruct(feedback_id='FEEDBACK-M50A-001',operating_state_id='OPERATING-STATE-M49A-001',request_id='M50A-FEEDBACK-REQUEST-001',intent='RECONSTRUCT_EXECUTION_FEEDBACK')
 return AdaptiveFeedbackChainService(path)

def run(svc):
 rows=[]
 for stage,aid,pid,rid,_ in CHAIN: rows.append(svc.reconstruct(stage=stage,authority_id=aid,parent_id=pid,request_id=rid,intent=f'RECONSTRUCT_{stage}'))
 return rows

def test_m51_m55_full_chain_exactly_once_replay_restart(tmp_path):
 path=tmp_path/'adaptive.sqlite3'; svc=fixture(path); first=run(svc); second=run(svc); third=run(AdaptiveFeedbackChainService(path))
 assert first==second==third
 for row,spec in zip(first,CHAIN): assert spec[4] in row.values()
 with svc.database.read_connection() as c:
  for spec in CHAIN: assert c.execute('SELECT COUNT(*) n FROM replay_defense_history WHERE request_id=?',(spec[3],)).fetchone()['n']==1

def test_m51_m55_requires_accepted_parent_and_blocks_second(tmp_path):
 svc=fixture(tmp_path/'blocked.sqlite3')
 with pytest.raises(AdaptiveFeedbackBlocked): svc.reconstruct(stage='EXECUTION_OUTCOME',authority_id='BAD',parent_id='UNKNOWN',request_id='BAD-REQ',intent='RECONSTRUCT_EXECUTION_OUTCOME')
 run(svc)
 with pytest.raises(AdaptiveFeedbackBlocked): svc.reconstruct(stage='EXECUTION_OUTCOME',authority_id='SECOND',parent_id='FEEDBACK-M50A-001',request_id='SECOND-REQ',intent='RECONSTRUCT_EXECUTION_OUTCOME')

def test_m51_m55_history_append_only(tmp_path):
 svc=fixture(tmp_path/'append.sqlite3'); run(svc)
 with pytest.raises(sqlite3.IntegrityError):
  with svc.database.transaction() as c: c.execute('DELETE FROM adaptive_operating_states_history')

def test_m51_m55_zero_upstream_mutation(tmp_path):
 svc=fixture(tmp_path/'preserve.sqlite3'); tables=('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_ledger_postings','business_ledger_balances','business_performance_summaries','business_performance_intelligence','business_decisions','action_plans','business_priorities','execution_queues','operating_commands','business_operating_states','execution_feedback')
 with svc.database.read_connection() as c: before=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables)
 run(svc)
 with svc.database.read_connection() as c: after=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables)
 assert before==after
