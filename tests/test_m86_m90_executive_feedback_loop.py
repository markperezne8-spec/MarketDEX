from services.executive_feedback_loop_service import ExecutiveFeedbackLoopService

EXPECTED = (
    ('EXECUTIVE_CYCLE_OBSERVATION', 'EXECUTIVE_CYCLE_OBSERVATION_READY'),
    ('EXECUTIVE_PERFORMANCE_RECONSTRUCTION', 'EXECUTIVE_PERFORMANCE_READY'),
    ('EXECUTIVE_VARIANCE_AUTHORITY', 'EXECUTIVE_VARIANCE_READY'),
    ('EXECUTIVE_RESPONSE_AUTHORITY', 'EXECUTIVE_RESPONSE_READY'),
    ('EXECUTIVE_FEEDBACK_LOOP_AUTHORITY', 'EXECUTIVE_FEEDBACK_LOOP_READY'),
)

def test_m86_m90_stage_contract_is_ordered_and_complete():
    assert ExecutiveFeedbackLoopService.stage_contract() == EXPECTED
    assert len({stage for stage, _ in EXPECTED}) == 5
    assert len({result for _, result in EXPECTED}) == 5

def test_m90_declares_executive_feedback_loop_ready():
    assert ExecutiveFeedbackLoopService.final_result() == 'EXECUTIVE_FEEDBACK_LOOP_READY'
