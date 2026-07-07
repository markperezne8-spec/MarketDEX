from services.executive_accountability_cycle_service import ExecutiveAccountabilityCycleService

EXPECTED=(('EXECUTIVE_STEWARDSHIP_OBSERVATION','EXECUTIVE_STEWARDSHIP_OBSERVATION_READY'),('EXECUTIVE_ACCOUNTABILITY_RECONSTRUCTION','EXECUTIVE_ACCOUNTABILITY_READY'),('EXECUTIVE_RESPONSIBILITY_AUTHORITY','EXECUTIVE_RESPONSIBILITY_READY'),('EXECUTIVE_ANSWERABILITY_AUTHORITY','EXECUTIVE_ANSWERABILITY_READY'),('EXECUTIVE_ACCOUNTABILITY_CYCLE_AUTHORITY','EXECUTIVE_ACCOUNTABILITY_CYCLE_READY'))

def test_m151_m155_stage_contract_is_ordered_and_complete():
 assert ExecutiveAccountabilityCycleService.stage_contract()==EXPECTED
 assert len({x for x,_ in EXPECTED})==5
 assert len({x for _,x in EXPECTED})==5

def test_m155_declares_executive_accountability_cycle_ready():
 assert ExecutiveAccountabilityCycleService.final_result()=='EXECUTIVE_ACCOUNTABILITY_CYCLE_READY'
