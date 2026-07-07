import sqlite3
import pytest
from services.m45_m49_acceptance_service import M45M49AcceptanceService
from services.execution_feedback_service import ExecutionFeedbackService
from services.adaptive_feedback_chain_service import AdaptiveFeedbackChainService
from services.continuous_business_loop_service import ContinuousBusinessLoopService, ContinuousBusinessLoopBlocked

ADAPTIVE=(('EXECUTION_OUTCOME','OUTCOME-M51-001','FEEDBACK-M50A-001','M51-REQUEST-001'),('VARIANCE_INTELLIGENCE','VARIANCE-M52-001','OUTCOME-M51-001','M52-REQUEST-001'),('OPERATING_ADJUSTMENT','ADJUSTMENT-M53-001','VARIANCE-M52-001','M53-REQUEST-001'),('ADAPTIVE_COMMAND','ADAPTIVE-COMMAND-M54-001','ADJUSTMENT-M53-001','M54-REQUEST-001'),('ADAPTIVE_OPERATING_STATE','ADAPTIVE-STATE-M55-001','ADAPTIVE-COMMAND-M54-001','M55-REQUEST-001'))
CHAIN=(('BUSINESS_LOOP_OBSERVATION','OBSERVATION-M56-001','ADAPTIVE-STATE-M55-001','M56-REQUEST-001','OBSERVATION_READY'),('ADAPTIVE_PERFORMANCE_RECONSTRUCTION','PERFORMANCE-M57-001','OBSERVATION-M56-001','M57-REQUEST-001','PERFORMANCE_READY'),('STRATEGIC_VARIANCE_AUTHORITY','STRATEGIC-VARIANCE-M58-001','PERFORMANCE-M57-001','M58-REQUEST-001','STRATEGIC_VARIANCE_READY'),('BUSINESS_RESPONSE_AUTHORITY','RESPONSE-M59-001','STRATEGIC-VARIANCE-M58-001','M59-REQUEST-001','RESPONSE_READY'),('CONTINUOUS_OPERATING_LOOP_AUTHORITY','LOOP-M60-001','RESPONSE-M59-001','M60-REQUEST-001','CONTINUOUS_OPERATING_READY'))

def fixture(path):
 assert M45M49AcceptanceService(path).execute()['passed']==21
 ExecutionFeedbackService(path).reconstruct(feedback_id='FEEDBACK-M50A-001',operating_state_id='OPERATING-STATE-M49A-001',request_id='M50A-FEEDBACK-REQUEST-001',intent='RECONSTRUCT_EXECUTION_FEEDBACK')
 adaptive=AdaptiveFeedbackChainService(path)
 for stage,aid,pid,rid in ADAPTIVE: adaptive.reconstruct(stage=stage,authority_id=aid,parent_id=pid,request_id=rid,intent=f'RECONSTRUCT_{stage}')
 return ContinuousBusinessLoopService(path)

def run(svc):
 return [svc.reconstruct(stage=stage,authority_id=aid,parent_id=pid,request_id=rid,intent=f'RECONSTRUCT_{stage}') for stage,aid,pid,rid,_ in CHAIN]

def test_m56_m60_full_chain_exactly_once_replay_restart(tmp_path):
 path=tmp_path/'loop.sqlite3'; svc=fixture(path); first=run(svc); second=run(svc); third=run(ContinuousBusinessLoopService(path))
 assert first==second==third
 for row,spec in zip(first,CHAIN): assert spec[4] in row.values()
 with svc.database.read_connection() as c:
  for spec in CHAIN: assert c.execute('SELECT COUNT(*) n FROM replay_defense_history WHERE request_id=?',(spec[3],)).fetchone()['n']==1

def test_m56_m60_requires_accepted_parent_and_blocks_second(tmp_path):
 svc=fixture(tmp_path/'blocked.sqlite3')
 with pytest.raises(ContinuousBusinessLoopBlocked): svc.reconstruct(stage='BUSINESS_LOOP_OBSERVATION',authority_id='BAD',parent_id='UNKNOWN',request_id='BAD-REQ',intent='RECONSTRUCT_BUSINESS_LOOP_OBSERVATION')
 run(svc)
 with pytest.raises(ContinuousBusinessLoopBlocked): svc.reconstruct(stage='BUSINESS_LOOP_OBSERVATION',authority_id='SECOND',parent_id='ADAPTIVE-STATE-M55-001',request_id='SECOND-REQ',intent='RECONSTRUCT_BUSINESS_LOOP_OBSERVATION')

def test_m56_m60_history_append_only(tmp_path):
 svc=fixture(tmp_path/'append.sqlite3'); run(svc)
 with pytest.raises(sqlite3.IntegrityError):
  with svc.database.transaction() as c: c.execute('DELETE FROM continuous_operating_loops_history')

def test_m56_m60_zero_upstream_mutation(tmp_path):
 svc=fixture(tmp_path/'preserve.sqlite3'); tables=('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_ledger_postings','business_ledger_balances','business_performance_summaries','business_performance_intelligence','business_decisions','action_plans','business_priorities','execution_queues','operating_commands','business_operating_states','execution_feedback','execution_outcomes','variance_intelligence','operating_adjustments','adaptive_commands','adaptive_operating_states')
 with svc.database.read_connection() as c: before=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables)
 run(svc)
 with svc.database.read_connection() as c: after=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables)
 assert before==after
