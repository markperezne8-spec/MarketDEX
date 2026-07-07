import sqlite3
import pytest
from services.m45_m49_acceptance_service import M45M49AcceptanceService
from services.execution_feedback_service import ExecutionFeedbackService
from services.adaptive_feedback_chain_service import AdaptiveFeedbackChainService
from services.continuous_business_loop_service import ContinuousBusinessLoopService
from services.autonomous_business_cycle_service import AutonomousBusinessCycleService
from services.strategic_control_loop_service import StrategicControlLoopService
from services.governed_strategic_cycle_service import GovernedStrategicCycleService
from services.enterprise_governance_loop_service import EnterpriseGovernanceLoopService, EnterpriseGovernanceLoopBlocked

CHAINS=((AdaptiveFeedbackChainService,(('EXECUTION_OUTCOME','OUTCOME-M51-001','FEEDBACK-M50A-001','M51-REQUEST-001'),('VARIANCE_INTELLIGENCE','VARIANCE-M52-001','OUTCOME-M51-001','M52-REQUEST-001'),('OPERATING_ADJUSTMENT','ADJUSTMENT-M53-001','VARIANCE-M52-001','M53-REQUEST-001'),('ADAPTIVE_COMMAND','ADAPTIVE-COMMAND-M54-001','ADJUSTMENT-M53-001','M54-REQUEST-001'),('ADAPTIVE_OPERATING_STATE','ADAPTIVE-STATE-M55-001','ADAPTIVE-COMMAND-M54-001','M55-REQUEST-001'))),(ContinuousBusinessLoopService,(('BUSINESS_LOOP_OBSERVATION','OBSERVATION-M56-001','ADAPTIVE-STATE-M55-001','M56-REQUEST-001'),('ADAPTIVE_PERFORMANCE_RECONSTRUCTION','PERFORMANCE-M57-001','OBSERVATION-M56-001','M57-REQUEST-001'),('STRATEGIC_VARIANCE_AUTHORITY','STRATEGIC-VARIANCE-M58-001','PERFORMANCE-M57-001','M58-REQUEST-001'),('BUSINESS_RESPONSE_AUTHORITY','RESPONSE-M59-001','STRATEGIC-VARIANCE-M58-001','M59-REQUEST-001'),('CONTINUOUS_OPERATING_LOOP_AUTHORITY','LOOP-M60-001','RESPONSE-M59-001','M60-REQUEST-001'))),(AutonomousBusinessCycleService,(('OPERATING_LOOP_EVALUATION','EVALUATION-M61-001','LOOP-M60-001','M61-REQUEST-001'),('BUSINESS_CYCLE_DECISION','CYCLE-DECISION-M62-001','EVALUATION-M61-001','M62-REQUEST-001'),('AUTONOMOUS_ACTION_AUTHORITY','AUTONOMOUS-ACTION-M63-001','CYCLE-DECISION-M62-001','M63-REQUEST-001'),('AUTONOMOUS_EXECUTION_AUTHORITY','AUTONOMOUS-EXECUTION-M64-001','AUTONOMOUS-ACTION-M63-001','M64-REQUEST-001'),('AUTONOMOUS_BUSINESS_CYCLE_AUTHORITY','AUTONOMOUS-CYCLE-M65-001','AUTONOMOUS-EXECUTION-M64-001','M65-REQUEST-001'))),(StrategicControlLoopService,(('BUSINESS_CYCLE_OBSERVATION','CYCLE-OBSERVATION-M66-001','AUTONOMOUS-CYCLE-M65-001','M66-REQUEST-001'),('AUTONOMOUS_PERFORMANCE_RECONSTRUCTION','AUTONOMOUS-PERFORMANCE-M67-001','CYCLE-OBSERVATION-M66-001','M67-REQUEST-001'),('STRATEGIC_CONTROL_VARIANCE','CONTROL-VARIANCE-M68-001','AUTONOMOUS-PERFORMANCE-M67-001','M68-REQUEST-001'),('STRATEGIC_CONTROL_RESPONSE','CONTROL-RESPONSE-M69-001','CONTROL-VARIANCE-M68-001','M69-REQUEST-001'),('STRATEGIC_CONTROL_LOOP_AUTHORITY','CONTROL-LOOP-M70-001','CONTROL-RESPONSE-M69-001','M70-REQUEST-001'))),(GovernedStrategicCycleService,(('STRATEGIC_LOOP_EVALUATION','STRATEGIC-EVALUATION-M71-001','CONTROL-LOOP-M70-001','M71-REQUEST-001'),('GOVERNANCE_DECISION_AUTHORITY','GOVERNANCE-DECISION-M72-001','STRATEGIC-EVALUATION-M71-001','M72-REQUEST-001'),('GOVERNED_ACTION_AUTHORITY','GOVERNED-ACTION-M73-001','GOVERNANCE-DECISION-M72-001','M73-REQUEST-001'),('GOVERNED_EXECUTION_AUTHORITY','GOVERNED-EXECUTION-M74-001','GOVERNED-ACTION-M73-001','M74-REQUEST-001'),('GOVERNED_STRATEGIC_CYCLE_AUTHORITY','GOVERNED-CYCLE-M75-001','GOVERNED-EXECUTION-M74-001','M75-REQUEST-001'))))
CHAIN=(('GOVERNED_CYCLE_OBSERVATION','GOVERNED-OBSERVATION-M76-001','GOVERNED-CYCLE-M75-001','M76-REQUEST-001','GOVERNED_CYCLE_OBSERVATION_READY'),('ENTERPRISE_PERFORMANCE_RECONSTRUCTION','ENTERPRISE-PERFORMANCE-M77-001','GOVERNED-OBSERVATION-M76-001','M77-REQUEST-001','ENTERPRISE_PERFORMANCE_READY'),('ENTERPRISE_GOVERNANCE_VARIANCE','ENTERPRISE-VARIANCE-M78-001','ENTERPRISE-PERFORMANCE-M77-001','M78-REQUEST-001','ENTERPRISE_GOVERNANCE_VARIANCE_READY'),('ENTERPRISE_GOVERNANCE_RESPONSE','ENTERPRISE-RESPONSE-M79-001','ENTERPRISE-VARIANCE-M78-001','M79-REQUEST-001','ENTERPRISE_GOVERNANCE_RESPONSE_READY'),('ENTERPRISE_GOVERNANCE_LOOP_AUTHORITY','ENTERPRISE-LOOP-M80-001','ENTERPRISE-RESPONSE-M79-001','M80-REQUEST-001','ENTERPRISE_GOVERNANCE_LOOP_READY'))

def fixture(path):
 assert M45M49AcceptanceService(path).execute()['passed']==21
 ExecutionFeedbackService(path).reconstruct(feedback_id='FEEDBACK-M50A-001',operating_state_id='OPERATING-STATE-M49A-001',request_id='M50A-FEEDBACK-REQUEST-001',intent='RECONSTRUCT_EXECUTION_FEEDBACK')
 for cls,chain in CHAINS:
  service=cls(path)
  for stage,aid,pid,rid in chain: service.reconstruct(stage=stage,authority_id=aid,parent_id=pid,request_id=rid,intent=f'RECONSTRUCT_{stage}')
 return EnterpriseGovernanceLoopService(path)

def run(svc): return [svc.reconstruct(stage=s,authority_id=a,parent_id=p,request_id=r,intent=f'RECONSTRUCT_{s}') for s,a,p,r,_ in CHAIN]

def test_m76_m80_full_chain_exactly_once_replay_restart(tmp_path):
 path=tmp_path/'enterprise.sqlite3'; svc=fixture(path); first=run(svc); second=run(svc); third=run(EnterpriseGovernanceLoopService(path)); assert first==second==third
 for row,spec in zip(first,CHAIN): assert spec[4] in row.values()
 with svc.database.read_connection() as c:
  for spec in CHAIN: assert c.execute('SELECT COUNT(*) n FROM replay_defense_history WHERE request_id=?',(spec[3],)).fetchone()['n']==1

def test_m76_m80_requires_parent_and_blocks_second(tmp_path):
 svc=fixture(tmp_path/'blocked.sqlite3')
 with pytest.raises(EnterpriseGovernanceLoopBlocked): svc.reconstruct(stage='GOVERNED_CYCLE_OBSERVATION',authority_id='BAD',parent_id='UNKNOWN',request_id='BAD-REQ',intent='RECONSTRUCT_GOVERNED_CYCLE_OBSERVATION')
 run(svc)
 with pytest.raises(EnterpriseGovernanceLoopBlocked): svc.reconstruct(stage='GOVERNED_CYCLE_OBSERVATION',authority_id='SECOND',parent_id='GOVERNED-CYCLE-M75-001',request_id='SECOND-REQ',intent='RECONSTRUCT_GOVERNED_CYCLE_OBSERVATION')

def test_m76_m80_history_append_only(tmp_path):
 svc=fixture(tmp_path/'append.sqlite3'); run(svc)
 with pytest.raises(sqlite3.IntegrityError):
  with svc.database.transaction() as c: c.execute('DELETE FROM enterprise_governance_loops_history')

def test_m76_m80_zero_upstream_mutation(tmp_path):
 svc=fixture(tmp_path/'preserve.sqlite3'); tables=('sales','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_decisions','operating_commands','adaptive_operating_states','continuous_operating_loops','autonomous_business_cycles','strategic_control_loops','governed_strategic_cycles')
 with svc.database.read_connection() as c: before={t:c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables}
 run(svc)
 with svc.database.read_connection() as c: after={t:c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables}
 assert before==after
