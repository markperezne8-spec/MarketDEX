from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from services.base_service import AuthoritativeService

class ExecutiveControlCycleBlocked(RuntimeError): pass

STAGES=(
('ENTERPRISE_LOOP_EVALUATION','enterprise_governance_loops','enterprise_loop_id','enterprise_loop_result','ENTERPRISE_GOVERNANCE_LOOP_READY','enterprise_loop_evaluations','enterprise_evaluation_id','enterprise_loop_id','ENTERPRISE_LOOP_EVALUATION_READY'),
('EXECUTIVE_DECISION_AUTHORITY','enterprise_loop_evaluations','enterprise_evaluation_id','enterprise_evaluation_result','ENTERPRISE_LOOP_EVALUATION_READY','executive_decisions','executive_decision_id','enterprise_evaluation_id','EXECUTIVE_DECISION_READY'),
('EXECUTIVE_ACTION_AUTHORITY','executive_decisions','executive_decision_id','executive_decision_result','EXECUTIVE_DECISION_READY','executive_actions','executive_action_id','executive_decision_id','EXECUTIVE_ACTION_READY'),
('EXECUTIVE_EXECUTION_AUTHORITY','executive_actions','executive_action_id','executive_action_result','EXECUTIVE_ACTION_READY','executive_executions','executive_execution_id','executive_action_id','EXECUTIVE_EXECUTION_READY'),
('EXECUTIVE_CONTROL_CYCLE_AUTHORITY','executive_executions','executive_execution_id','executive_execution_result','EXECUTIVE_EXECUTION_READY','executive_control_cycles','executive_cycle_id','executive_execution_id','EXECUTIVE_CONTROL_CYCLE_READY'))

class ExecutiveControlCycleService(AuthoritativeService):
 service_name='executive_control_cycle_service'
 def __init__(self,path):
  self.path=Path(path); self.database=DatabaseManager(self.path); self.database.initialize(); self.events=EventRepository(); super().__init__(self.database,self.events)
  with self.database.transaction() as c:
   for stage,_,_,_,_,table,idcol,parentcol,result in STAGES:
    rc=self._rc(table); rq=f'{idcol}_request_id'; ec=f'{idcol}_event_id'; h=f'{table}_history'
    c.executescript(f'''CREATE TABLE IF NOT EXISTS {table}({idcol} TEXT PRIMARY KEY,{parentcol} TEXT NOT NULL UNIQUE,{rq} TEXT NOT NULL UNIQUE,{ec} TEXT NOT NULL UNIQUE,authority_code TEXT NOT NULL,authority_reason TEXT NOT NULL,{rc} TEXT NOT NULL CHECK({rc}='{result}'),created_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS {h}(history_id INTEGER PRIMARY KEY AUTOINCREMENT,{idcol} TEXT NOT NULL,{parentcol} TEXT NOT NULL,{ec} TEXT NOT NULL,authority_code TEXT NOT NULL,{rc} TEXT NOT NULL CHECK({rc}='{result}'),recorded_at TEXT NOT NULL,UNIQUE({ec},{rc})); CREATE TRIGGER IF NOT EXISTS {table}_no_update BEFORE UPDATE ON {table} BEGIN SELECT RAISE(ABORT,'{table} is append-only'); END; CREATE TRIGGER IF NOT EXISTS {table}_no_delete BEFORE DELETE ON {table} BEGIN SELECT RAISE(ABORT,'{table} is append-only'); END; CREATE TRIGGER IF NOT EXISTS {h}_no_update BEFORE UPDATE ON {h} BEGIN SELECT RAISE(ABORT,'{h} is append-only'); END; CREATE TRIGGER IF NOT EXISTS {h}_no_delete BEFORE DELETE ON {h} BEGIN SELECT RAISE(ABORT,'{h} is append-only'); END;''')
 def _rc(self,t): return {'enterprise_loop_evaluations':'enterprise_evaluation_result','executive_decisions':'executive_decision_result','executive_actions':'executive_action_result','executive_executions':'executive_execution_result','executive_control_cycles':'executive_cycle_result'}[t]
 def reconstruct(self,*,stage,authority_id,parent_id,request_id,intent):
  stage=str(stage).upper(); s=next((x for x in STAGES if x[0]==stage),None)
  if not s or not all(str(v).strip() for v in(authority_id,parent_id,request_id)) or str(intent).upper()!=f'RECONSTRUCT_{stage}': raise ExecutiveControlCycleBlocked('Explicit complete executive control authority required')
  et,pt,pid,prc,pr,t,idc,pc,r=s; rc=self._rc(t); rq=f'{idc}_request_id'; ec=f'{idc}_event_id'; event=self._new_event(et,request_id,{'authority_id':authority_id,'parent_id':parent_id,'stage':stage})
  with self.database.read_connection() as c:
   prior=c.execute('SELECT * FROM event_identity WHERE request_id=?',(request_id,)).fetchone()
   if prior:
    row=c.execute(f'SELECT * FROM {t} WHERE {rq}=?',(request_id,)).fetchone()
    if row and row[idc]==authority_id and prior['payload_sha256']==event.payload_sha256: self._replay(prior,et); return self.get(stage,authority_id)
    raise ExecutiveControlCycleBlocked(f'{stage} request identity mismatch')
  with self.database.transaction() as c:
   if not c.execute(f'SELECT 1 FROM {pt} WHERE {pid}=? AND {prc}=?',(parent_id,pr)).fetchone(): raise ExecutiveControlCycleBlocked(f'Accepted {pr} authority required')
   if c.execute(f'SELECT 1 FROM {t} WHERE {pc}=?',(parent_id,)).fetchone(): raise ExecutiveControlCycleBlocked(f'Second {stage} authority blocked')
   preserved=('sales','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_decisions','operating_commands','adaptive_operating_states','continuous_operating_loops','autonomous_business_cycles','strategic_control_loops','governed_strategic_cycles','enterprise_governance_loops'); before=tuple(c.execute(f'SELECT COUNT(*) n FROM {x}').fetchone()['n'] for x in preserved); code=f'AUTHORIZE_{stage}'
   self._append_event_and_audit(c,event,f'reconstruct_{stage.lower()}'); c.execute(f'INSERT INTO {t}({idc},{pc},{rq},{ec},authority_code,authority_reason,{rc},created_at) VALUES (?,?,?,?,?,?,?,?)',(authority_id,parent_id,request_id,event.event_id,code,f'Accepted bounded {stage.lower()} authority',r,event.committed_at)); c.execute(f'INSERT INTO {t}_history({idc},{pc},{ec},authority_code,{rc},recorded_at) VALUES (?,?,?,?,?,?)',(authority_id,parent_id,event.event_id,code,r,event.committed_at)); c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,et,authority_id,'VERIFIED',event.committed_at)); self._verify_event(c,event)
   if before!=tuple(c.execute(f'SELECT COUNT(*) n FROM {x}').fetchone()['n'] for x in preserved): raise RuntimeError(f'{stage} mutated preserved authority')
  return self.get(stage,authority_id)
 def _replay(self,p,e):
  with self.database.transaction() as c: c.execute("INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES (?,?,?,?, 'BLOCKED',?)",(p['request_id'],p['event_id'],e,p['payload_sha256'],p['committed_at']))
 def get(self,stage,authority_id):
  s=next(x for x in STAGES if x[0]==str(stage).upper()); t,idc=s[5],s[6]
  with self.database.read_connection() as c:
   row=c.execute(f'SELECT * FROM {t} WHERE {idc}=?',(authority_id,)).fetchone(); n=c.execute(f'SELECT COUNT(*) n FROM {t}_history WHERE {idc}=?',(authority_id,)).fetchone()['n']
   if not row or n!=1: raise ExecutiveControlCycleBlocked(f'{stage} reconstruction failed')
   return dict(row)
