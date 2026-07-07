from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from services.base_service import AuthoritativeService

class ExecutiveEvolutionCycleBlocked(RuntimeError): pass

STAGES=(
('EXECUTIVE_LEARNING_OBSERVATION','executive_learning_cycles','executive_learning_cycle_id','executive_learning_cycle_result','EXECUTIVE_LEARNING_CYCLE_READY','executive_learning_observations','executive_learning_observation_id','executive_learning_cycle_id','executive_learning_observation_result','EXECUTIVE_LEARNING_OBSERVATION_READY'),
('EXECUTIVE_EVOLUTION_RECONSTRUCTION','executive_learning_observations','executive_learning_observation_id','executive_learning_observation_result','EXECUTIVE_LEARNING_OBSERVATION_READY','executive_evolution_reconstructions','executive_evolution_id','executive_learning_observation_id','executive_evolution_result','EXECUTIVE_EVOLUTION_READY'),
('EXECUTIVE_CAPABILITY_AUTHORITY','executive_evolution_reconstructions','executive_evolution_id','executive_evolution_result','EXECUTIVE_EVOLUTION_READY','executive_capabilities','executive_capability_id','executive_evolution_id','executive_capability_result','EXECUTIVE_CAPABILITY_READY'),
('EXECUTIVE_TRANSFORMATION_AUTHORITY','executive_capabilities','executive_capability_id','executive_capability_result','EXECUTIVE_CAPABILITY_READY','executive_transformations','executive_transformation_id','executive_capability_id','executive_transformation_result','EXECUTIVE_TRANSFORMATION_READY'),
('EXECUTIVE_EVOLUTION_CYCLE_AUTHORITY','executive_transformations','executive_transformation_id','executive_transformation_result','EXECUTIVE_TRANSFORMATION_READY','executive_evolution_cycles','executive_evolution_cycle_id','executive_transformation_id','executive_evolution_cycle_result','EXECUTIVE_EVOLUTION_CYCLE_READY'))

class ExecutiveEvolutionCycleService(AuthoritativeService):
 service_name='executive_evolution_cycle_service'
 def __init__(self,path):
  self.path=Path(path); self.database=DatabaseManager(self.path); self.database.initialize(); self.events=EventRepository(); super().__init__(self.database,self.events)
  with self.database.transaction() as c:
   for _,_,_,_,_,t,idc,pc,rc,r in STAGES:
    rq=f'{idc}_request_id'; ec=f'{idc}_event_id'; h=f'{t}_history'; literal=r.replace("'", "''")
    c.execute(f"CREATE TABLE IF NOT EXISTS {t}({idc} TEXT PRIMARY KEY,{pc} TEXT NOT NULL UNIQUE,{rq} TEXT NOT NULL UNIQUE,{ec} TEXT NOT NULL UNIQUE,authority_code TEXT NOT NULL,{rc} TEXT NOT NULL CHECK({rc}='{literal}'),created_at TEXT NOT NULL)")
    c.execute(f'CREATE TABLE IF NOT EXISTS {h}(history_id INTEGER PRIMARY KEY AUTOINCREMENT,{idc} TEXT NOT NULL,{pc} TEXT NOT NULL,{ec} TEXT NOT NULL UNIQUE,{rc} TEXT NOT NULL,recorded_at TEXT NOT NULL)')
    for name,table,op in ((f'{t}_no_update',t,'UPDATE'),(f'{t}_no_delete',t,'DELETE'),(f'{h}_no_update',h,'UPDATE'),(f'{h}_no_delete',h,'DELETE')): c.execute(f"CREATE TRIGGER IF NOT EXISTS {name} BEFORE {op} ON {table} BEGIN SELECT RAISE(ABORT,'append-only'); END")
 def reconstruct(self,*,stage,authority_id,parent_id,request_id,intent):
  stage=str(stage).upper(); s=next((x for x in STAGES if x[0]==stage),None)
  if not s or not all(str(v).strip() for v in(authority_id,parent_id,request_id)) or str(intent).upper()!=f'RECONSTRUCT_{stage}': raise ExecutiveEvolutionCycleBlocked('Explicit complete executive evolution authority required')
  et,pt,pid,prc,pr,t,idc,pc,rc,r=s; rq=f'{idc}_request_id'; ec=f'{idc}_event_id'; event=self._new_event(et,request_id,{'authority_id':authority_id,'parent_id':parent_id,'stage':stage})
  with self.database.read_connection() as c:
   prior=c.execute('SELECT * FROM event_identity WHERE request_id=?',(request_id,)).fetchone()
   if prior:
    row=c.execute(f'SELECT * FROM {t} WHERE {rq}=?',(request_id,)).fetchone()
    if row and row[idc]==authority_id and prior['payload_sha256']==event.payload_sha256: self._replay(prior,et); return self.get(stage,authority_id)
    raise ExecutiveEvolutionCycleBlocked(f'{stage} request identity mismatch')
  with self.database.transaction() as c:
   if not c.execute(f'SELECT 1 FROM {pt} WHERE {pid}=? AND {prc}=?',(parent_id,pr)).fetchone(): raise ExecutiveEvolutionCycleBlocked(f'Accepted {pr} authority required')
   if c.execute(f'SELECT 1 FROM {t} WHERE {pc}=?',(parent_id,)).fetchone(): raise ExecutiveEvolutionCycleBlocked(f'Second {stage} authority blocked')
   preserved=('sales','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_decisions','operating_commands','adaptive_operating_states','continuous_operating_loops','autonomous_business_cycles','strategic_control_loops','governed_strategic_cycles','enterprise_governance_loops','executive_control_cycles','executive_feedback_loops','executive_learning_cycles'); before=tuple(c.execute(f'SELECT COUNT(*) n FROM {x}').fetchone()['n'] for x in preserved)
   self._append_event_and_audit(c,event,f'reconstruct_{stage.lower()}'); c.execute(f'INSERT INTO {t}({idc},{pc},{rq},{ec},authority_code,{rc},created_at) VALUES (?,?,?,?,?,?,?)',(authority_id,parent_id,request_id,event.event_id,f'AUTHORIZE_{stage}',r,event.committed_at)); c.execute(f'INSERT INTO {t}_history({idc},{pc},{ec},{rc},recorded_at) VALUES (?,?,?,?,?)',(authority_id,parent_id,event.event_id,r,event.committed_at)); c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,et,authority_id,'VERIFIED',event.committed_at)); self._verify_event(c,event)
   if before!=tuple(c.execute(f'SELECT COUNT(*) n FROM {x}').fetchone()['n'] for x in preserved): raise RuntimeError(f'{stage} mutated preserved authority')
  return self.get(stage,authority_id)
 def _replay(self,p,e):
  with self.database.transaction() as c: c.execute("INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES (?,?,?,?, 'BLOCKED',?)",(p['request_id'],p['event_id'],e,p['payload_sha256'],p['committed_at']))
 def get(self,stage,authority_id):
  s=next(x for x in STAGES if x[0]==str(stage).upper()); t,idc=s[5],s[6]
  with self.database.read_connection() as c:
   row=c.execute(f'SELECT * FROM {t} WHERE {idc}=?',(authority_id,)).fetchone(); n=c.execute(f'SELECT COUNT(*) n FROM {t}_history WHERE {idc}=?',(authority_id,)).fetchone()['n']
   if not row or n!=1: raise ExecutiveEvolutionCycleBlocked(f'{stage} reconstruction failed')
   return dict(row)
 @staticmethod
 def stage_contract(): return tuple((x[0],x[-1]) for x in STAGES)
 @staticmethod
 def final_result(): return STAGES[-1][-1]
