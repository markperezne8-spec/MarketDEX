from services.executive_control_cycle_service import ExecutiveControlCycleService, ExecutiveControlCycleBlocked

STAGES = (
    ('EXECUTIVE_CYCLE_OBSERVATION', 'EXECUTIVE_CYCLE_OBSERVATION_READY'),
    ('EXECUTIVE_PERFORMANCE_RECONSTRUCTION', 'EXECUTIVE_PERFORMANCE_READY'),
    ('EXECUTIVE_VARIANCE_AUTHORITY', 'EXECUTIVE_VARIANCE_READY'),
    ('EXECUTIVE_RESPONSE_AUTHORITY', 'EXECUTIVE_RESPONSE_READY'),
    ('EXECUTIVE_FEEDBACK_LOOP_AUTHORITY', 'EXECUTIVE_FEEDBACK_LOOP_READY'),
)

class ExecutiveFeedbackLoopBlocked(ExecutiveControlCycleBlocked):
    pass

class ExecutiveFeedbackLoopService(ExecutiveControlCycleService):
    service_name = 'executive_feedback_loop_service'

    @staticmethod
    def stage_contract():
        return STAGES

    @staticmethod
    def final_result():
        return 'EXECUTIVE_FEEDBACK_LOOP_READY'
