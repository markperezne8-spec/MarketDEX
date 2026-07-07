from services.executive_covenant_cycle_service import ExecutiveCovenantCycleService

EXPECTED=(('EXECUTIVE_INSTITUTION_OBSERVATION','EXECUTIVE_INSTITUTION_OBSERVATION_READY'),('EXECUTIVE_COVENANT_RECONSTRUCTION','EXECUTIVE_COVENANT_READY'),('EXECUTIVE_MANDATE_AUTHORITY','EXECUTIVE_MANDATE_READY'),('EXECUTIVE_FIDUCIARY_AUTHORITY','EXECUTIVE_FIDUCIARY_READY'),('EXECUTIVE_COVENANT_CYCLE_AUTHORITY','EXECUTIVE_COVENANT_CYCLE_READY'))

def test_m126_m130_stage_contract_is_ordered_and_complete():
 assert ExecutiveCovenantCycleService.stage_contract()==EXPECTED
 assert len({x for x,_ in EXPECTED})==5
 assert len({x for _,x in EXPECTED})==5

def test_m130_declares_executive_covenant_cycle_ready():
 assert ExecutiveCovenantCycleService.final_result()=='EXECUTIVE_COVENANT_CYCLE_READY'
