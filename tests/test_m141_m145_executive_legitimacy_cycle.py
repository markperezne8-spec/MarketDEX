from services.executive_legitimacy_cycle_service import ExecutiveLegitimacyCycleService

EXPECTED=(('EXECUTIVE_SOVEREIGNTY_OBSERVATION','EXECUTIVE_SOVEREIGNTY_OBSERVATION_READY'),('EXECUTIVE_LEGITIMACY_RECONSTRUCTION','EXECUTIVE_LEGITIMACY_READY'),('EXECUTIVE_CONSENT_AUTHORITY','EXECUTIVE_CONSENT_READY'),('EXECUTIVE_TRUST_AUTHORITY','EXECUTIVE_TRUST_READY'),('EXECUTIVE_LEGITIMACY_CYCLE_AUTHORITY','EXECUTIVE_LEGITIMACY_CYCLE_READY'))

def test_m141_m145_stage_contract_is_ordered_and_complete():
 assert ExecutiveLegitimacyCycleService.stage_contract()==EXPECTED
 assert len({x for x,_ in EXPECTED})==5
 assert len({x for _,x in EXPECTED})==5

def test_m145_declares_executive_legitimacy_cycle_ready():
 assert ExecutiveLegitimacyCycleService.final_result()=='EXECUTIVE_LEGITIMACY_CYCLE_READY'
