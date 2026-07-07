from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from services.base_service import AuthoritativeService

class ExecutiveConstitutionalCycleBlocked(RuntimeError): pass

STAGES=(
('EXECUTIVE_COVENANT_OBSERVATION','executive_covenant_cycles','executive_covenant_cycle_id','executive_covenant_cycle_result','EXECUTIVE_COVENANT_CYCLE_READY','executive_covenant_observations','executive_covenant_observation_id','executive_covenant_cycle_id','executive_covenant_observation_result','EXECUTIVE_COVENANT_OBSERVATION_READY'),
('EXECUTIVE_CONSTITUTIONAL_RECONSTRUCTION','executive_covenant_observations','executive_covenant_observation_id','executive_covenant_observation_result','EXECUTIVE_COVENANT_OBSERVATION_READY','executive_constitutional_reconstructions','executive_constitutional_id','executive_covenant_observation_id','executive_constitutional_result','EXECUTIVE_CONSTITUTIONAL_READY'),
('EXECUTIVE_PRINCIPLE_AUTHORITY','executive_constitutional_reconstructions','executive_constitutional_id','executive_constitutional_result','EXECUTIVE_CONSTITUTIONAL_READY','executive_principle_authorities','executive_principle_id','executive_constitutional_id','executive_principle_result','EXECUTIVE_PRINCIPLE_READY'),
('EXECUTIVE_BOUNDARY_AUTHORITY','executive_principle_authorities','executive_principle_id','executive_principle_result','EXECUTIVE_PRINCIPLE_READY','executive_boundary_authorities','executive_boundary_id','executive_principle_id','executive_boundary_result','EXECUTIVE_BOUNDARY_READY'),
('EXECUTIVE_CONSTITUTIONAL_CYCLE_AUTHORITY','executive_boundary_authorities','executive_boundary_id','executive_boundary_result','EXECUTIVE_BOUNDARY_READY','executive_constitutional_cycles','executive_constitutional_cycle_id','executive_boundary_id','executive_constitutional_cycle_result','EXECUTIVE_CONSTITUTIONAL_CYCLE_READY'))

class ExecutiveConstitutionalCycleService(AuthoritativeService):
 service_name='executive_constitutional_cycle_service'
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
  if not s or not all(str(v).strip() for v in(authority_id,parent_id,request_id)) or str(intent).upper()!=f'RECONSTRUCT_{stage}': raise ExecutiveConstitutionalCycleBlocked('Explicit complete executive constitutional authority required')
  et,pt,pid,prc,pr,t,idc,pc,rc,r=s; rq=f'{idc}_request_id'; event=self._new_event(et,request_id,{'authority_id':authority_id,'parent_id':parent_id,'stage':stage})
  with self.database.read_connection() as c:
   prior=c.execute('SELECT * FROM event_identity WHERE request_id=?',(request_id,)).fetchone()
   if prior:
    row=c.execute(f'SELECT * FROM {t} WHERE {rq}=?',(request_id,)).fetchone()
    if row and row[idc]==authority_id and prior['payload_sha256']==event.payload_sha256: self._replay(prior,et); return self.get(stage,authority_id)
    raise ExecutiveConstitutionalCycleBlocked(f'{stage} request identity mismatch')
  with self.database.transaction() as c:
   if not c.execute(f'SELECT 1 FROM {pt} WHERE {pid}=? AND {prc}=?',(parent_id,pr)).fetchone(): raise ExecutiveConstitutionalCycleBlocked(f'Accepted {pr} authority required')
   if c.execute(f'SELECT 1 FROM {t} WHERE {pc}=?',(parent_id,)).fetchone(): raise ExecutiveConstitutionalCycleBlocked(f'Second {stage} authority blocked')
   preserved=('sales','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_decisions','operating_commands','adaptive_operating_states','continuous_operating_loops','autonomous_business_cycles','strategic_control_loops','governed_strategic_cycles','enterprise_governance_loops','executive_control_cycles','executive_feedback_loops','executive_learning_cycles','executive_evolution_cycles','executive_renewal_cycles','executive_continuity_cycles','executive_succession_cycles','executive_perpetuity_cycles','executive_institution_cycles','executive_covenant_cycles'); before=tuple(c.execute(f'SELECT COUNT(*) n FROM {x}').fetchone()['n'] for x in preserved)
   self._append_event_and_audit(c,event,f'reconstruct_{stage.lower()}'); ec=f'{idc}_event_id'; c.execute(f'INSERT INTO {t}({idc},{pc},{rq},{ec},authority_code,{rc},created_at) VALUES (?,?,?,?,?,?,?)',(authority_id,parent_id,request_id,event.event_id,f'AUTHORIZE_{stage}',r,event.committed_at)); c.execute(f'INSERT INTO {t}_history({idc},{pc},{ec},{rc},recorded_at) VALUES (?,?,?,?,?)',(authority_id,parent_id,event.event_id,r,event.committed_at)); c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,et,authority_id,'VERIFIED',event.committed_at)); self._verify_event(c,event)
   if before!=tuple(c.execute(f'SELECT COUNT(*) n FROM {x}').fetchone()['n'] for x in preserved): raise RuntimeError(f'{stage} mutated preserved authority')
  return self.get(stage,authority_id)
 def _replay(self,p,e):
  with self.database.transaction() as c: c.execute("INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES (?,?,?,?, 'BLOCKED',?)",(p['request_id'],p['event_id'],e,p['payload_sha256'],p['committed_at']))
 def get(self,stage,authority_id):
  s=next(x for x in STAGES if x[0]==str(stage).upper()); t,idc=s[5],s[6]
  with self.database.read_connection() as c:
   row=c.execute(f'SELECT * FROM {t} WHERE {idc}=?',(authority_id,)).fetchone(); n=c.execute(f'SELECT COUNT(*) n FROM {t}_history WHERE {idc}=?',(authority_id,)).fetchone()['n']
   if not row or n!=1: raise ExecutiveConstitutionalCycleBlocked(f'{stage} reconstruction failed')
   return dict(row)
 @staticmethod
 def stage_contract(): return tuple((x[0],x[-1]) for x in STAGES)
 @staticmethod
 def final_result(): return STAGES[-1][-1]
