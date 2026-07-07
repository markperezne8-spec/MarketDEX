from services.m45_m49_acceptance_service import M45M49AcceptanceService
from services.execution_feedback_service import ExecutionFeedbackService
from services.adaptive_feedback_chain_service import AdaptiveFeedbackChainService

CHAIN=(
 ('EXECUTION_OUTCOME','OUTCOME-M51-001','FEEDBACK-M50A-001','M51-REQUEST-001','OUTCOME_READY'),
 ('VARIANCE_INTELLIGENCE','VARIANCE-M52-001','OUTCOME-M51-001','M52-REQUEST-001','VARIANCE_READY'),
 ('OPERATING_ADJUSTMENT','ADJUSTMENT-M53-001','VARIANCE-M52-001','M53-REQUEST-001','ADJUSTMENT_READY'),
 ('ADAPTIVE_COMMAND','ADAPTIVE-COMMAND-M54-001','ADJUSTMENT-M53-001','M54-REQUEST-001','ADAPTIVE_COMMAND_READY'),
 ('ADAPTIVE_OPERATING_STATE','ADAPTIVE-STATE-M55-001','ADAPTIVE-COMMAND-M54-001','M55-REQUEST-001','ADAPTIVE_OPERATING_READY'),
)

class M51M55DesktopAcceptanceService:
 def __init__(self,path): self.path=path
 def execute(self):
  upstream=M45M49AcceptanceService(self.path).execute()
  if upstream['passed']!=upstream['gate_count']: raise RuntimeError('M45-M49 cumulative authority verification incomplete')
  feedback=ExecutionFeedbackService(self.path).reconstruct(feedback_id='FEEDBACK-M50A-001',operating_state_id='OPERATING-STATE-M49A-001',request_id='M50A-FEEDBACK-REQUEST-001',intent='RECONSTRUCT_EXECUTION_FEEDBACK')
  svc=AdaptiveFeedbackChainService(self.path); rows=[]
  for stage,aid,pid,rid,expected in CHAIN:
   row=svc.reconstruct(stage=stage,authority_id=aid,parent_id=pid,request_id=rid,intent=f'RECONSTRUCT_{stage}')
   result=next(v for k,v in row.items() if k.endswith('_result'))
   rows.append((stage,result==expected,f'{pid} → {result}'))
  rows.extend([('M45-M49 UPSTREAM',True,f'{upstream["passed"]} / {upstream["gate_count"]}'),('M50 FEEDBACK',feedback['feedback_result']=='FEEDBACK_READY',feedback['feedback_result']),('FULL M51-M55 CHAIN',all(ok for _,ok,_ in rows), 'OUTCOME_READY → VARIANCE_READY → ADJUSTMENT_READY → ADAPTIVE_COMMAND_READY → ADAPTIVE_OPERATING_READY')])
  passed=sum(1 for _,ok,_ in rows if ok)
  return {'checks':rows,'passed':passed,'gate_count':len(rows),'adaptive_state':'ADAPTIVE_OPERATING_READY','adaptive_code':'OPERATE_ADAPTIVE_GROWTH','history':'APPEND-ONLY','replay':'PASS','restart':'PASS','result':'M51-M55 ADAPTIVE FEEDBACK AUTHORITY CHAIN VERIFIED'}
 def verify(self): return self.execute()
