import sqlite3
import pytest
from services.executive_transparency_cycle_service import ExecutiveTransparencyCycleService
from services.executive_integrity_cycle_service import ExecutiveIntegrityCycleBlocked, ExecutiveIntegrityCycleService

EXPECTED=(('EXECUTIVE_TRANSPARENCY_OBSERVATION','EXECUTIVE_TRANSPARENCY_OBSERVATION_READY'),('EXECUTIVE_INTEGRITY_RECONSTRUCTION','EXECUTIVE_INTEGRITY_READY'),('EXECUTIVE_ETHICAL_AUTHORITY','EXECUTIVE_ETHICAL_READY'),('EXECUTIVE_FIDELITY_AUTHORITY','EXECUTIVE_FIDELITY_READY'),('EXECUTIVE_INTEGRITY_CYCLE_AUTHORITY','EXECUTIVE_INTEGRITY_CYCLE_READY'))

def test_m161_m165_stage_contract_is_ordered_and_complete():
 assert ExecutiveIntegrityCycleService.stage_contract()==EXPECTED
 assert len({x for x,_ in EXPECTED})==5 and len({x for _,x in EXPECTED})==5

def test_m165_declares_executive_integrity_cycle_ready(): assert ExecutiveIntegrityCycleService.final_result()=='EXECUTIVE_INTEGRITY_CYCLE_READY'

def _seed_transparency(service):
 ExecutiveTransparencyCycleService(service.path)
 with service.database.transaction() as c:
  c.execute("INSERT INTO executive_transparency_cycles(executive_transparency_cycle_id,executive_visibility_id,executive_transparency_cycle_id_request_id,executive_transparency_cycle_id_event_id,authority_code,executive_transparency_cycle_result,created_at) VALUES (?,?,?,?,?,?,?)",('transparency-cycle-1','visibility-1','seed-request','seed-event','AUTHORIZE_EXECUTIVE_TRANSPARENCY_CYCLE_AUTHORITY','EXECUTIVE_TRANSPARENCY_CYCLE_READY','2026-07-07T00:00:00Z'))

def _build(service):
 parent='transparency-cycle-1'; ids=('observation-1','integrity-1','ethical-1','fidelity-1','cycle-1')
 for (stage,_),authority_id in zip(EXPECTED,ids):
  service.reconstruct(stage=stage,authority_id=authority_id,parent_id=parent,request_id=f'request-{authority_id}',intent=f'RECONSTRUCT_{stage}'); parent=authority_id
 return ids

def test_m161_requires_accepted_transparency_parent(tmp_path):
 path=tmp_path/'m165.sqlite3'; ExecutiveTransparencyCycleService(path); service=ExecutiveIntegrityCycleService(path)
 with pytest.raises(ExecutiveIntegrityCycleBlocked,match='Accepted EXECUTIVE_TRANSPARENCY_CYCLE_READY authority required'):
  service.reconstruct(stage=EXPECTED[0][0],authority_id='observation-1',parent_id='missing',request_id='request-1',intent='RECONSTRUCT_EXECUTIVE_TRANSPARENCY_OBSERVATION')

def test_m161_m165_exactly_once_replay_audit_and_restart(tmp_path):
 path=tmp_path/'m165.sqlite3'; service=ExecutiveIntegrityCycleService(path); _seed_transparency(service); ids=_build(service)
 row=service.reconstruct(stage=EXPECTED[-1][0],authority_id=ids[-1],parent_id=ids[-2],request_id='request-cycle-1',intent='RECONSTRUCT_EXECUTIVE_INTEGRITY_CYCLE_AUTHORITY')
 assert row['executive_integrity_cycle_result']=='EXECUTIVE_INTEGRITY_CYCLE_READY'
 with service.database.read_connection() as c:
  assert c.execute("SELECT COUNT(*) n FROM audit_events WHERE authority_type IN ('EXECUTIVE_TRANSPARENCY_OBSERVATION','EXECUTIVE_INTEGRITY_RECONSTRUCTION','EXECUTIVE_ETHICAL_AUTHORITY','EXECUTIVE_FIDELITY_AUTHORITY','EXECUTIVE_INTEGRITY_CYCLE_AUTHORITY') AND verification_result='VERIFIED'").fetchone()['n']==5
  assert c.execute("SELECT COUNT(*) n FROM replay_defense_history WHERE request_id='request-cycle-1' AND defense_result='BLOCKED'").fetchone()['n']==1
 service=ExecutiveIntegrityCycleService(path); assert service.get(EXPECTED[-1][0],ids[-1])['executive_integrity_cycle_result']=='EXECUTIVE_INTEGRITY_CYCLE_READY'

def test_m161_m165_identity_mismatch_and_second_authority_blocked(tmp_path):
 service=ExecutiveIntegrityCycleService(tmp_path/'m165.sqlite3'); _seed_transparency(service); stage=EXPECTED[0][0]
 service.reconstruct(stage=stage,authority_id='observation-1',parent_id='transparency-cycle-1',request_id='request-1',intent=f'RECONSTRUCT_{stage}')
 with pytest.raises(ExecutiveIntegrityCycleBlocked,match='request identity mismatch'): service.reconstruct(stage=stage,authority_id='observation-2',parent_id='transparency-cycle-1',request_id='request-1',intent=f'RECONSTRUCT_{stage}')
 with pytest.raises(ExecutiveIntegrityCycleBlocked,match='Second EXECUTIVE_TRANSPARENCY_OBSERVATION authority blocked'): service.reconstruct(stage=stage,authority_id='observation-2',parent_id='transparency-cycle-1',request_id='request-2',intent=f'RECONSTRUCT_{stage}')

def test_m161_m165_static_result_check_rejects_invalid_result(tmp_path):
 service=ExecutiveIntegrityCycleService(tmp_path/'m165.sqlite3')
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c: c.execute("INSERT INTO executive_integrity_cycles(executive_integrity_cycle_id,executive_fidelity_id,executive_integrity_cycle_id_request_id,executive_integrity_cycle_id_event_id,authority_code,executive_integrity_cycle_result,created_at) VALUES (?,?,?,?,?,?,?)",('cycle-x','fidelity-x','request-x','event-x','AUTHORITY','INVALID','2026-07-07T00:00:00Z'))
