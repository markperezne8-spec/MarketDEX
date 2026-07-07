from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from services.base_service import AuthoritativeService

class EnterpriseGovernanceLoopBlocked(RuntimeError): pass

STAGES=(
 ('GOVERNED_CYCLE_OBSERVATION','governed_strategic_cycles','governed_cycle_id','governed_cycle_result','GOVERNED_STRATEGIC_CYCLE_READY','governed_cycle_observations','governed_observation_id','governed_cycle_id','GOVERNED_CYCLE_OBSERVATION_READY'),
 ('ENTERPRISE_PERFORMANCE_RECONSTRUCTION','governed_cycle_observations','governed_observation_id','governed_observation_result','GOVERNED_CYCLE_OBSERVATION_READY','enterprise_performance_reconstructions','enterprise_performance_id','governed_observation_id','ENTERPRISE_PERFORMANCE_READY'),
 ('ENTERPRISE_GOVERNANCE_VARIANCE','enterprise_performance_reconstructions','enterprise_performance_id','enterprise_performance_result','ENTERPRISE_PERFORMANCE_READY','enterprise_governance_variances','enterprise_variance_id','enterprise_performance_id','ENTERPRISE_GOVERNANCE_VARIANCE_READY'),
 ('ENTERPRISE_GOVERNANCE_RESPONSE','enterprise_governance_variances','enterprise_variance_id','enterprise_variance_result','ENTERPRISE_GOVERNANCE_VARIANCE_READY','enterprise_governance_responses','enterprise_response_id','enterprise_variance_id','ENTERPRISE_GOVERNANCE_RESPONSE_READY'),
 ('ENTERPRISE_GOVERNANCE_LOOP_AUTHORITY','enterprise_governance_responses','enterprise_response_id','enterprise_response_result','ENTERPRISE_GOVERNANCE_RESPONSE_READY','enterprise_governance_loops','enterprise_loop_id','enterprise_response_id','ENTERPRISE_GOVERNANCE_LOOP_READY'),
)

class EnterpriseGovernanceLoopService(AuthoritativeService):
 service_name='enterprise_governance_loop_service'
 def __init__(self,path):
  self.path=Path(path); self.database=DatabaseManager(self.path); self.database.initialize(); self.events=EventRepository(); super().__init__(self.database,self.events)
  with self.database.transaction() as c:
   for event_type,_,_,_,_,table,idcol,parentcol,result in STAGES:
    hist=f'{table}_history'; resultcol=self._result_col(table); requestcol=f'{idcol}_request_id'; eventcol=f'{idcol}_event_id'
    c.executescript(f'''CREATE TABLE IF NOT EXISTS {table}({idcol} TEXT PRIMARY KEY,{parentcol} TEXT NOT NULL UNIQUE,{requestcol} TEXT NOT NULL UNIQUE,{eventcol} TEXT NOT NULL UNIQUE,authority_code TEXT NOT NULL,authority_reason TEXT NOT NULL,{resultcol} TEXT NOT NULL CHECK({resultcol}='{result}'),created_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS {hist}(history_id INTEGER PRIMARY KEY AUTOINCREMENT,{idcol} TEXT NOT NULL,{parentcol} TEXT NOT NULL,{eventcol} TEXT NOT NULL,authority_code TEXT NOT NULL,{resultcol} TEXT NOT NULL CHECK({resultcol}='{result}'),recorded_at TEXT NOT NULL,UNIQUE({eventcol},{resultcol})); CREATE TRIGGER IF NOT EXISTS {table}_no_update BEFORE UPDATE ON {table} BEGIN SELECT RAISE(ABORT,'{table} is append-only'); END; CREATE TRIGGER IF NOT EXISTS {table}_no_delete BEFORE DELETE ON {table} BEGIN SELECT RAISE(ABORT,'{table} is append-only'); END; CREATE TRIGGER IF NOT EXISTS {hist}_no_update BEFORE UPDATE ON {hist} BEGIN SELECT RAISE(ABORT,'{hist} is append-only'); END; CREATE TRIGGER IF NOT EXISTS {hist}_no_delete BEFORE DELETE ON {hist} BEGIN SELECT RAISE(ABORT,'{hist} is append-only'); END;''')
 def _result_col(self,t): return {'governed_cycle_observations':'governed_observation_result','enterprise_performance_reconstructions':'enterprise_performance_result','enterprise_governance_variances':'enterprise_variance_result','enterprise_governance_responses':'enterprise_response_result','enterprise_governance_loops':'enterprise_loop_result'}[t]
 def reconstruct(self,*,stage,authority_id,parent_id,request_id,intent):
  stage=str(stage).upper(); spec=next((x for x in STAGES if x[0]==stage),None)
  if not spec or not all(str(v).strip() for v in (authority_id,parent_id,request_id)) or str(intent).upper()!=f'RECONSTRUCT_{stage}': raise EnterpriseGovernanceLoopBlocked('Explicit complete enterprise governance authority required')
  event_type,parent_table,parent_idcol,parent_resultcol,parent_result,table,idcol,parentcol,result=spec; resultcol=self._result_col(table); requestcol=f'{idcol}_request_id'; eventcol=f'{idcol}_event_id'; payload={'authority_id':authority_id,'parent_id':parent_id,'stage':stage}; event=self._new_event(event_type,request_id,payload)
  with self.database.read_connection() as c:
   prior=c.execute('SELECT * FROM event_identity WHERE request_id=?',(request_id,)).fetchone()
   if prior:
    row=c.execute(f'SELECT * FROM {table} WHERE {requestcol}=?',(request_id,)).fetchone()
    if row and row[idcol]==authority_id and prior['payload_sha256']==event.payload_sha256: self._replay(prior,event_type); return self.get(stage,authority_id)
    raise EnterpriseGovernanceLoopBlocked(f'{stage} request identity mismatch')
  with self.database.transaction() as c:
   parent=c.execute(f'SELECT * FROM {parent_table} WHERE {parent_idcol}=? AND {parent_resultcol}=?',(parent_id,parent_result)).fetchone()
   if not parent: raise EnterpriseGovernanceLoopBlocked(f'Accepted {parent_result} authority required')
   if c.execute(f'SELECT 1 FROM {table} WHERE {parentcol}=?',(parent_id,)).fetchone(): raise EnterpriseGovernanceLoopBlocked(f'Second {stage} authority blocked')
   code,reason=self._derive(stage); preserved=('sales','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_ledger_postings','business_ledger_balances','business_performance_summaries','business_performance_intelligence','business_decisions','action_plans','business_priorities','execution_queues','operating_commands','business_operating_states','execution_feedback','execution_outcomes','variance_intelligence','operating_adjustments','adaptive_commands','adaptive_operating_states','business_loop_observations','adaptive_performance_reconstructions','strategic_variances','business_responses','continuous_operating_loops','operating_loop_evaluations','business_cycle_decisions','autonomous_actions','autonomous_executions','autonomous_business_cycles','business_cycle_observations','autonomous_performance_reconstructions','strategic_control_variances','strategic_control_responses','strategic_control_loops','strategic_loop_evaluations','governance_decisions','governed_actions','governed_executions','governed_strategic_cycles'); before=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in preserved)
   self._append_event_and_audit(c,event,f'reconstruct_{stage.lower()}'); c.execute(f'INSERT INTO {table}({idcol},{parentcol},{requestcol},{eventcol},authority_code,authority_reason,{resultcol},created_at) VALUES (?,?,?,?,?,?,?,?)',(authority_id,parent_id,request_id,event.event_id,code,reason,result,event.committed_at)); c.execute(f'INSERT INTO {table}_history({idcol},{parentcol},{eventcol},authority_code,{resultcol},recorded_at) VALUES (?,?,?,?,?,?)',(authority_id,parent_id,event.event_id,code,result,event.committed_at)); c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,event_type,authority_id,'VERIFIED',event.committed_at)); self._verify_event(c,event)
   after=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in preserved)
   if before!=after: raise RuntimeError(f'{stage} mutated preserved authority')
  return self.get(stage,authority_id)
 def _derive(self,stage):
  return {'GOVERNED_CYCLE_OBSERVATION':('OBSERVE_GOVERNED_STRATEGIC_CYCLE','Observe accepted governed strategic cycle without mutation'),'ENTERPRISE_PERFORMANCE_RECONSTRUCTION':('RECONSTRUCT_ENTERPRISE_PERFORMANCE','Reconstruct enterprise performance from accepted governed cycle observation'),'ENTERPRISE_GOVERNANCE_VARIANCE':('AUTHORIZE_ENTERPRISE_GOVERNANCE_VARIANCE','Authorize enterprise governance variance from accepted performance'),'ENTERPRISE_GOVERNANCE_RESPONSE':('AUTHORIZE_ENTERPRISE_GOVERNANCE_RESPONSE','Translate accepted enterprise variance into bounded response'),'ENTERPRISE_GOVERNANCE_LOOP_AUTHORITY':('OPERATE_ENTERPRISE_GOVERNANCE_LOOP','Declare enterprise governance loop ready')}[stage]
 def _replay(self,prior,event_type):
  with self.database.transaction() as c: c.execute("INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES (?,?,?,?, 'BLOCKED',?)",(prior['request_id'],prior['event_id'],event_type,prior['payload_sha256'],prior['committed_at']))
 def get(self,stage,authority_id):
  spec=next(x for x in STAGES if x[0]==str(stage).upper()); table=spec[5]; idcol=spec[6]; hist=f'{table}_history'
  with self.database.read_connection() as c:
   row=c.execute(f'SELECT * FROM {table} WHERE {idcol}=?',(authority_id,)).fetchone(); h=c.execute(f'SELECT COUNT(*) n FROM {hist} WHERE {idcol}=?',(authority_id,)).fetchone()['n']
   if not row or h!=1: raise EnterpriseGovernanceLoopBlocked(f'{stage} reconstruction failed')
   return dict(row)
