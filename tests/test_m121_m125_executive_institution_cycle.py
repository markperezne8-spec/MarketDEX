from services.executive_institution_cycle_service import ExecutiveInstitutionCycleService

EXPECTED=(('EXECUTIVE_PERPETUITY_OBSERVATION','EXECUTIVE_PERPETUITY_OBSERVATION_READY'),('EXECUTIVE_INSTITUTION_RECONSTRUCTION','EXECUTIVE_INSTITUTION_READY'),('EXECUTIVE_CHARTER_AUTHORITY','EXECUTIVE_CHARTER_READY'),('EXECUTIVE_DOCTRINE_AUTHORITY','EXECUTIVE_DOCTRINE_READY'),('EXECUTIVE_INSTITUTION_CYCLE_AUTHORITY','EXECUTIVE_INSTITUTION_CYCLE_READY'))

def test_m121_m125_stage_contract_is_ordered_and_complete():
 assert ExecutiveInstitutionCycleService.stage_contract()==EXPECTED
 assert len({x for x,_ in EXPECTED})==5
 assert len({x for _,x in EXPECTED})==5

def test_m125_declares_executive_institution_cycle_ready():
 assert ExecutiveInstitutionCycleService.final_result()=='EXECUTIVE_INSTITUTION_CYCLE_READY'
