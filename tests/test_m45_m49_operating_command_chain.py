import sqlite3
import pytest
from services.m45_m49_acceptance_service import M45M49AcceptanceService,CHAIN,ACCEPTANCE_GATE_COUNT
from services.m44a_acceptance_service import M44AAcceptanceService
from services.operating_command_chain_service import OperatingCommandChainService,OperatingChainBlocked,STAGES

def fixture(path):
 assert M44AAcceptanceService(path).execute()['passed']==12
 return OperatingCommandChainService(path)
def run_chain(svc):
 for stage,aid,pid,rid,_,_ in CHAIN: svc.reconstruct(stage=stage,authority_id=aid,parent_id=pid,request_id=rid,intent=f'RECONSTRUCT_{stage}')
def test_accelerated_chain_exact_acceptance_21_of_21(tmp_path):
 r=M45M49AcceptanceService(tmp_path/'m45_m49.sqlite3').execute(); assert r['passed']==ACCEPTANCE_GATE_COUNT==21; assert r['gate_count']==21; assert r['operating_state']=='OPERATING_READY'; assert r['operating_code']=='OPERATE_CONTROLLED_GROWTH'; assert r['result']=='M45-M49 OPERATING COMMAND CHAIN VERIFIED'
def test_replay_restart_exactly_once_for_every_stage(tmp_path):
 path=tmp_path/'replay.sqlite3'; svc=fixture(path)
 for stage,aid,pid,rid,_,_ in CHAIN:
  k=dict(stage=stage,authority_id=aid,parent_id=pid,request_id=rid,intent=f'RECONSTRUCT_{stage}'); a=svc.reconstruct(**k); b=svc.reconstruct(**k); svc=OperatingCommandChainService(path); d=svc.reconstruct(**k); assert a==b==d
 with svc.database.read_connection() as c:
  for spec in STAGES: assert c.execute(f'SELECT COUNT(*) n FROM {spec[5]}').fetchone()['n']==1; assert c.execute(f'SELECT COUNT(*) n FROM {spec[5]}_history').fetchone()['n']==1
def test_lineage_fail_closed_and_second_authority_blocked(tmp_path):
 svc=fixture(tmp_path/'blocked.sqlite3'); stage,aid,pid,rid,_,_=CHAIN[0]
 with pytest.raises(OperatingChainBlocked): svc.reconstruct(stage=stage,authority_id=aid,parent_id='UNKNOWN',request_id=rid,intent=f'RECONSTRUCT_{stage}')
 svc.reconstruct(stage=stage,authority_id=aid,parent_id=pid,request_id=rid,intent=f'RECONSTRUCT_{stage}')
 with pytest.raises(OperatingChainBlocked): svc.reconstruct(stage=stage,authority_id='SECOND',parent_id=pid,request_id='SECOND-REQUEST',intent=f'RECONSTRUCT_{stage}')
def test_zero_upstream_mutation_across_full_chain(tmp_path):
 svc=fixture(tmp_path/'zero.sqlite3'); tables=('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_ledger_postings','business_ledger_balances','business_performance_summaries','business_performance_intelligence','business_decisions')
 def counts(c): return tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables)
 with svc.database.read_connection() as c: before=counts(c)
 run_chain(svc)
 with svc.database.read_connection() as c: after=counts(c)
 assert before==after
def test_all_stage_histories_append_only(tmp_path):
 svc=fixture(tmp_path/'append.sqlite3'); run_chain(svc)
 for spec in STAGES:
  with pytest.raises(sqlite3.IntegrityError):
   with svc.database.transaction() as c: c.execute(f'DELETE FROM {spec[5]}_history')
