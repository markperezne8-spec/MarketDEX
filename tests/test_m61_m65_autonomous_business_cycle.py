import sqlite3
import pytest
from services.m45_m49_acceptance_service import M45M49AcceptanceService
from services.execution_feedback_service import ExecutionFeedbackService
from services.adaptive_feedback_chain_service import AdaptiveFeedbackChainService
from services.continuous_business_loop_service import ContinuousBusinessLoopService
from services.autonomous_business_cycle_service import AutonomousBusinessCycleService, AutonomousBusinessCycleBlocked

ADAPTIVE=(('EXECUTION_OUTCOME','OUTCOME-M51-001','FEEDBACK-M50A-001','M51-REQUEST-001'),('VARIANCE_INTELLIGENCE','VARIANCE-M52-001','OUTCOME-M51-001','M52-REQUEST-001'),('OPERATING_ADJUSTMENT','ADJUSTMENT-M53-001','VARIANCE-M52-001','M53-REQUEST-001'),('ADAPTIVE_COMMAND','ADAPTIVE-COMMAND-M54-001','ADJUSTMENT-M53-001','M54-REQUEST-001'),('ADAPTIVE_OPERATING_STATE','ADAPTIVE-STATE-M55-001','ADAPTIVE-COMMAND-M54-001','M55-REQUEST-001'))
CONTINUOUS=(('BUSINESS_LOOP_OBSERVATION','OBSERVATION-M56-001','ADAPTIVE-STATE-M55-001','M56-REQUEST-001'),('ADAPTIVE_PERFORMANCE_RECONSTRUCTION','PERFORMANCE-M57-001','OBSERVATION-M56-001','M57-REQUEST-001'),('STRATEGIC_VARIANCE_AUTHORITY','STRATEGIC-VARIANCE-M58-001','PERFORMANCE-M57-001','M58-REQUEST-001'),('BUSINESS_RESPONSE_AUTHORITY','RESPONSE-M59-001','STRATEGIC-VARIANCE-M58-001','M59-REQUEST-001'),('CONTINUOUS_OPERATING_LOOP_AUTHORITY','LOOP-M60-001','RESPONSE-M59-001','M60-REQUEST-001'))
CHAIN=(('OPERATING_LOOP_EVALUATION','EVALUATION-M61-001','LOOP-M60-001','M61-REQUEST-001','EVALUATION_READY'),('BUSINESS_CYCLE_DECISION','CYCLE-DECISION-M62-001','EVALUATION-M61-001','M62-REQUEST-001','CYCLE_DECISION_READY'),('AUTONOMOUS_ACTION_AUTHORITY','AUTONOMOUS-ACTION-M63-001','CYCLE-DECISION-M62-001','M63-REQUEST-001','AUTONOMOUS_ACTION_READY'),('AUTONOMOUS_EXECUTION_AUTHORITY','AUTONOMOUS-EXECUTION-M64-001','AUTONOMOUS-ACTION-M63-001','M64-REQUEST-001','AUTONOMOUS_EXECUTION_READY'),('AUTONOMOUS_BUSINESS_CYCLE_AUTHORITY','AUTONOMOUS-CYCLE-M65-001','AUTONOMOUS-EXECUTION-M64-001','M65-REQUEST-001','AUTONOMOUS_BUSINESS_CYCLE_READY'))

def fixture(path):
 assert M45M49AcceptanceService(path).execute()['passed']==21
 ExecutionFeedbackService(path).reconstruct(feedback_id='FEEDBACK-M50A-001',operating_state_id='OPERATING-STATE-M49A-001',request_id='M50A-FEEDBACK-REQUEST-001',intent='RECONSTRUCT_EXECUTION_FEEDBACK')
 adaptive=AdaptiveFeedbackChainService(path)
 for stage,aid,pid,rid in ADAPTIVE: adaptive.reconstruct(stage=stage,authority_id=aid,parent_id=pid,request_id=rid,intent=f'RECONSTRUCT_{stage}')
 continuous=ContinuousBusinessLoopService(path)
 for stage,aid,pid,rid in CONTINUOUS: continuous.reconstruct(stage=stage,authority_id=aid,parent_id=pid,request_id=rid,intent=f'RECONSTRUCT_{stage}')
 return AutonomousBusinessCycleService(path)

def run(svc): return [svc.reconstruct(stage=s,authority_id=a,parent_id=p,request_id=r,intent=f'RECONSTRUCT_{s}') for s,a,p,r,_ in CHAIN]

def test_m61_m65_full_chain_exactly_once_replay_restart(tmp_path):
 path=tmp_path/'cycle.sqlite3'; svc=fixture(path); first=run(svc); second=run(svc); third=run(AutonomousBusinessCycleService(path)); assert first==second==third
 for row,spec in zip(first,CHAIN): assert spec[4] in row.values()
 with svc.database.read_connection() as c:
  for spec in CHAIN: assert c.execute('SELECT COUNT(*) n FROM replay_defense_history WHERE request_id=?',(spec[3],)).fetchone()['n']==1

def test_m61_m65_requires_accepted_parent_and_blocks_second(tmp_path):
 svc=fixture(tmp_path/'blocked.sqlite3')
 with pytest.raises(AutonomousBusinessCycleBlocked): svc.reconstruct(stage='OPERATING_LOOP_EVALUATION',authority_id='BAD',parent_id='UNKNOWN',request_id='BAD-REQ',intent='RECONSTRUCT_OPERATING_LOOP_EVALUATION')
 run(svc)
 with pytest.raises(AutonomousBusinessCycleBlocked): svc.reconstruct(stage='OPERATING_LOOP_EVALUATION',authority_id='SECOND',parent_id='LOOP-M60-001',request_id='SECOND-REQ',intent='RECONSTRUCT_OPERATING_LOOP_EVALUATION')

def test_m61_m65_history_append_only(tmp_path):
 svc=fixture(tmp_path/'append.sqlite3'); run(svc)
 with pytest.raises(sqlite3.IntegrityError):
  with svc.database.transaction() as c: c.execute('DELETE FROM autonomous_business_cycles_history')

def test_m61_m65_zero_upstream_mutation(tmp_path):
 svc=fixture(tmp_path/'preserve.sqlite3'); tables=('sales','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_decisions','operating_commands','adaptive_operating_states','continuous_operating_loops')
 with svc.database.read_connection() as c: before={t:c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables}
 run(svc)
 with svc.database.read_connection() as c: after={t:c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables}
 assert before==after
