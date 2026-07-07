import sqlite3
import pytest
from services.executive_transparency_cycle_service import ExecutiveTransparencyCycleBlocked, ExecutiveTransparencyCycleService

EXPECTED=(('EXECUTIVE_ACCOUNTABILITY_OBSERVATION','EXECUTIVE_ACCOUNTABILITY_OBSERVATION_READY'),('EXECUTIVE_TRANSPARENCY_RECONSTRUCTION','EXECUTIVE_TRANSPARENCY_READY'),('EXECUTIVE_DISCLOSURE_AUTHORITY','EXECUTIVE_DISCLOSURE_READY'),('EXECUTIVE_VISIBILITY_AUTHORITY','EXECUTIVE_VISIBILITY_READY'),('EXECUTIVE_TRANSPARENCY_CYCLE_AUTHORITY','EXECUTIVE_TRANSPARENCY_CYCLE_READY'))

def test_m156_m160_stage_contract_is_ordered_and_complete():
 assert ExecutiveTransparencyCycleService.stage_contract()==EXPECTED
 assert len({x for x,_ in EXPECTED})==5
 assert len({x for _,x in EXPECTED})==5

def test_m160_declares_executive_transparency_cycle_ready():
 assert ExecutiveTransparencyCycleService.final_result()=='EXECUTIVE_TRANSPARENCY_CYCLE_READY'

def _seed_accountability(service):
 with service.database.transaction() as c:
  c.execute("INSERT INTO executive_accountability_cycles(executive_accountability_cycle_id,executive_answerability_id,executive_accountability_cycle_id_request_id,executive_accountability_cycle_id_event_id,authority_code,executive_accountability_cycle_result,created_at) VALUES (?,?,?,?,?,?,?)",('accountability-1','answerability-1','seed-request','seed-event','AUTHORIZE_EXECUTIVE_ACCOUNTABILITY_CYCLE_AUTHORITY','EXECUTIVE_ACCOUNTABILITY_CYCLE_READY','2026-07-07T00:00:00Z'))

def _build_cycle(service):
 parent='accountability-1'
 ids=('observation-1','transparency-1','disclosure-1','visibility-1','cycle-1')
 for (stage,_),authority_id in zip(EXPECTED,ids):
  service.reconstruct(stage=stage,authority_id=authority_id,parent_id=parent,request_id=f'request-{authority_id}',intent=f'RECONSTRUCT_{stage}')
  parent=authority_id
 return ids

def test_m156_requires_accepted_accountability_parent(tmp_path):
 service=ExecutiveTransparencyCycleService(tmp_path/'m160.sqlite3')
 with pytest.raises(ExecutiveTransparencyCycleBlocked,match='Accepted EXECUTIVE_ACCOUNTABILITY_CYCLE_READY authority required'):
  service.reconstruct(stage=EXPECTED[0][0],authority_id='observation-1',parent_id='missing',request_id='request-1',intent='RECONSTRUCT_EXECUTIVE_ACCOUNTABILITY_OBSERVATION')

def test_m156_m160_exactly_once_replay_audit_and_restart_reconstruction(tmp_path):
 path=tmp_path/'m160.sqlite3'; service=ExecutiveTransparencyCycleService(path); _seed_accountability(service); ids=_build_cycle(service)
 row=service.reconstruct(stage=EXPECTED[-1][0],authority_id=ids[-1],parent_id=ids[-2],request_id='request-cycle-1',intent='RECONSTRUCT_EXECUTIVE_TRANSPARENCY_CYCLE_AUTHORITY')
 assert row['executive_transparency_cycle_result']=='EXECUTIVE_TRANSPARENCY_CYCLE_READY'
 with service.database.read_connection() as c:
  assert c.execute("SELECT COUNT(*) n FROM audit_events WHERE authority_type IN ('EXECUTIVE_ACCOUNTABILITY_OBSERVATION','EXECUTIVE_TRANSPARENCY_RECONSTRUCTION','EXECUTIVE_DISCLOSURE_AUTHORITY','EXECUTIVE_VISIBILITY_AUTHORITY','EXECUTIVE_TRANSPARENCY_CYCLE_AUTHORITY') AND verification_result='VERIFIED'").fetchone()['n']==5
  assert c.execute("SELECT COUNT(*) n FROM replay_defense_history WHERE request_id='request-cycle-1' AND defense_result='BLOCKED'").fetchone()['n']==1
 service=ExecutiveTransparencyCycleService(path)
 assert service.get(EXPECTED[-1][0],ids[-1])['executive_transparency_cycle_result']=='EXECUTIVE_TRANSPARENCY_CYCLE_READY'

def test_m156_m160_request_identity_mismatch_and_second_authority_are_blocked(tmp_path):
 service=ExecutiveTransparencyCycleService(tmp_path/'m160.sqlite3'); _seed_accountability(service)
 stage=EXPECTED[0][0]
 service.reconstruct(stage=stage,authority_id='observation-1',parent_id='accountability-1',request_id='request-1',intent=f'RECONSTRUCT_{stage}')
 with pytest.raises(ExecutiveTransparencyCycleBlocked,match='request identity mismatch'):
  service.reconstruct(stage=stage,authority_id='observation-2',parent_id='accountability-1',request_id='request-1',intent=f'RECONSTRUCT_{stage}')
 with pytest.raises(ExecutiveTransparencyCycleBlocked,match='Second EXECUTIVE_ACCOUNTABILITY_OBSERVATION authority blocked'):
  service.reconstruct(stage=stage,authority_id='observation-2',parent_id='accountability-1',request_id='request-2',intent=f'RECONSTRUCT_{stage}')

def test_m156_m160_static_result_check_rejects_invalid_result(tmp_path):
 service=ExecutiveTransparencyCycleService(tmp_path/'m160.sqlite3')
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c:
   c.execute("INSERT INTO executive_transparency_cycles(executive_transparency_cycle_id,executive_visibility_id,executive_transparency_cycle_id_request_id,executive_transparency_cycle_id_event_id,authority_code,executive_transparency_cycle_result,created_at) VALUES (?,?,?,?,?,?,?)",('cycle-x','visibility-x','request-x','event-x','AUTHORITY','INVALID','2026-07-07T00:00:00Z'))
