from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from services.base_service import AuthoritativeService

class GovernedStrategicCycleBlocked(RuntimeError): pass

STAGES=(
 ('STRATEGIC_LOOP_EVALUATION','strategic_control_loops','control_loop_id','control_loop_result','STRATEGIC_CONTROL_LOOP_READY','strategic_loop_evaluations','strategic_evaluation_id','control_loop_id','STRATEGIC_LOOP_EVALUATION_READY'),
 ('GOVERNANCE_DECISION_AUTHORITY','strategic_loop_evaluations','strategic_evaluation_id','strategic_evaluation_result','STRATEGIC_LOOP_EVALUATION_READY','governance_decisions','governance_decision_id','strategic_evaluation_id','GOVERNANCE_DECISION_READY'),
 ('GOVERNED_ACTION_AUTHORITY','governance_decisions','governance_decision_id','governance_decision_result','GOVERNANCE_DECISION_READY','governed_actions','governed_action_id','governance_decision_id','GOVERNED_ACTION_READY'),
 ('GOVERNED_EXECUTION_AUTHORITY','governed_actions','governed_action_id','governed_action_result','GOVERNED_ACTION_READY','governed_executions','governed_execution_id','governed_action_id','GOVERNED_EXECUTION_READY'),
 ('GOVERNED_STRATEGIC_CYCLE_AUTHORITY','governed_executions','governed_execution_id','governed_execution_result','GOVERNED_EXECUTION_READY','governed_strategic_cycles','governed_cycle_id','governed_execution_id','GOVERNED_STRATEGIC_CYCLE_READY'),
)

class GovernedStrategicCycleService(AuthoritativeService):
 service_name='governed_strategic_cycle_service'
 def __init__(self,path):
  self.path=Path(path); self.database=DatabaseManager(self.path); self.database.initialize(); self.events=EventRepository(); super().__init__(self.database,self.events)
  with self.database.transaction() as c:
   for event_type,_,_,_,_,table,idcol,parentcol,result in STAGES:
    hist=f'{table}_history'; resultcol=self._result_col(table); requestcol=f'{idcol}_request_id'; eventcol=f'{idcol}_event_id'
    c.executescript(f'''CREATE TABLE IF NOT EXISTS {table}({idcol} TEXT PRIMARY KEY,{parentcol} TEXT NOT NULL UNIQUE,{requestcol} TEXT NOT NULL UNIQUE,{eventcol} TEXT NOT NULL UNIQUE,authority_code TEXT NOT NULL,authority_reason TEXT NOT NULL,{resultcol} TEXT NOT NULL CHECK({resultcol}='{result}'),created_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS {hist}(history_id INTEGER PRIMARY KEY AUTOINCREMENT,{idcol} TEXT NOT NULL,{parentcol} TEXT NOT NULL,{eventcol} TEXT NOT NULL,authority_code TEXT NOT NULL,{resultcol} TEXT NOT NULL CHECK({resultcol}='{result}'),recorded_at TEXT NOT NULL,UNIQUE({eventcol},{resultcol})); CREATE TRIGGER IF NOT EXISTS {table}_no_update BEFORE UPDATE ON {table} BEGIN SELECT RAISE(ABORT,'{table} is append-only'); END; CREATE TRIGGER IF NOT EXISTS {table}_no_delete BEFORE DELETE ON {table} BEGIN SELECT RAISE(ABORT,'{table} is append-only'); END; CREATE TRIGGER IF NOT EXISTS {hist}_no_update BEFORE UPDATE ON {hist} BEGIN SELECT RAISE(ABORT,'{hist} is append-only'); END; CREATE TRIGGER IF NOT EXISTS {hist}_no_delete BEFORE DELETE ON {hist} BEGIN SELECT RAISE(ABORT,'{hist} is append-only'); END;''')
 def _result_col(self,t): return {'strategic_loop_evaluations':'strategic_evaluation_result','governance_decisions':'governance_decision_result','governed_actions':'governed_action_result','governed_executions':'governed_execution_result','governed_strategic_cycles':'governed_cycle_result'}[t]
 def reconstruct(self,*,stage,authority_id,parent_id,request_id,intent):
  stage=str(stage).upper(); spec=next((x for x in STAGES if x[0]==stage),None)
  if not spec or not all(str(v).strip() for v in (authority_id,parent_id,request_id)) or str(intent).upper()!=f'RECONSTRUCT_{stage}': raise GovernedStrategicCycleBlocked('Explicit complete governed strategic cycle authority required')
  event_type,parent_table,parent_idcol,parent_resultcol,parent_result,table,idcol,parentcol,result=spec; resultcol=self._result_col(table); requestcol=f'{idcol}_request_id'; eventcol=f'{idcol}_event_id'; payload={'authority_id':authority_id,'parent_id':parent_id,'stage':stage}; event=self._new_event(event_type,request_id,payload)
  with self.database.read_connection() as c:
   prior=c.execute('SELECT * FROM event_identity WHERE request_id=?',(request_id,)).fetchone()
   if prior:
    row=c.execute(f'SELECT * FROM {table} WHERE {requestcol}=?',(request_id,)).fetchone()
    if row and row[idcol]==authority_id and prior['payload_sha256']==event.payload_sha256: self._replay(prior,event_type); return self.get(stage,authority_id)
    raise GovernedStrategicCycleBlocked(f'{stage} request identity mismatch')
  with self.database.transaction() as c:
   parent=c.execute(f'SELECT * FROM {parent_table} WHERE {parent_idcol}=? AND {parent_resultcol}=?',(parent_id,parent_result)).fetchone()
   if not parent: raise GovernedStrategicCycleBlocked(f'Accepted {parent_result} authority required')
   if c.execute(f'SELECT 1 FROM {table} WHERE {parentcol}=?',(parent_id,)).fetchone(): raise GovernedStrategicCycleBlocked(f'Second {stage} authority blocked')
   code,reason=self._derive(stage); preserved=('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_ledger_postings','business_ledger_balances','business_performance_summaries','business_performance_intelligence','business_decisions','action_plans','business_priorities','execution_queues','operating_commands','business_operating_states','execution_feedback','execution_outcomes','variance_intelligence','operating_adjustments','adaptive_commands','adaptive_operating_states','business_loop_observations','adaptive_performance_reconstructions','strategic_variances','business_responses','continuous_operating_loops','operating_loop_evaluations','business_cycle_decisions','autonomous_actions','autonomous_executions','autonomous_business_cycles','business_cycle_observations','autonomous_performance_reconstructions','strategic_control_variances','strategic_control_responses','strategic_control_loops'); before=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in preserved)
   self._append_event_and_audit(c,event,f'reconstruct_{stage.lower()}'); c.execute(f'INSERT INTO {table}({idcol},{parentcol},{requestcol},{eventcol},authority_code,authority_reason,{resultcol},created_at) VALUES (?,?,?,?,?,?,?,?)',(authority_id,parent_id,request_id,event.event_id,code,reason,result,event.committed_at)); c.execute(f'INSERT INTO {table}_history({idcol},{parentcol},{eventcol},authority_code,{resultcol},recorded_at) VALUES (?,?,?,?,?,?)',(authority_id,parent_id,event.event_id,code,result,event.committed_at)); c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,event_type,authority_id,'VERIFIED',event.committed_at)); self._verify_event(c,event)
   after=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in preserved)
   if before!=after: raise RuntimeError(f'{stage} mutated preserved authority')
  return self.get(stage,authority_id)
 def _derive(self,stage):
  return {'STRATEGIC_LOOP_EVALUATION':('EVALUATE_STRATEGIC_CONTROL_LOOP','Evaluate accepted strategic control loop without mutation'),'GOVERNANCE_DECISION_AUTHORITY':('AUTHORIZE_GOVERNANCE_DECISION','Authorize bounded governance decision from accepted evaluation'),'GOVERNED_ACTION_AUTHORITY':('AUTHORIZE_GOVERNED_ACTION','Authorize governed action from accepted decision'),'GOVERNED_EXECUTION_AUTHORITY':('AUTHORIZE_GOVERNED_EXECUTION','Authorize governed execution from accepted action'),'GOVERNED_STRATEGIC_CYCLE_AUTHORITY':('OPERATE_GOVERNED_STRATEGIC_CYCLE','Declare governed strategic cycle ready')}[stage]
 def _replay(self,prior,event_type):
  with self.database.transaction() as c: c.execute("INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES (?,?,?,?, 'BLOCKED',?)",(prior['request_id'],prior['event_id'],event_type,prior['payload_sha256'],prior['committed_at']))
 def get(self,stage,authority_id):
  spec=next(x for x in STAGES if x[0]==str(stage).upper()); table=spec[5]; idcol=spec[6]; hist=f'{table}_history'
  with self.database.read_connection() as c:
   row=c.execute(f'SELECT * FROM {table} WHERE {idcol}=?',(authority_id,)).fetchone(); h=c.execute(f'SELECT COUNT(*) n FROM {hist} WHERE {idcol}=?',(authority_id,)).fetchone()['n']
   if not row or h!=1: raise GovernedStrategicCycleBlocked(f'{stage} reconstruction failed')
   return dict(row)
