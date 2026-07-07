from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from services.base_service import AuthoritativeService

class OperatingChainBlocked(RuntimeError): pass

STAGES=(
 ('ACTION_PLAN','business_decisions','decision_id','decision_result','DECISION_READY','action_plans','action_plan_id','decision_id','ACTION_PLAN_READY'),
 ('BUSINESS_PRIORITY','action_plans','action_plan_id','action_plan_result','ACTION_PLAN_READY','business_priorities','priority_id','action_plan_id','PRIORITIZED'),
 ('EXECUTION_QUEUE','business_priorities','priority_id','priority_result','PRIORITIZED','execution_queues','execution_queue_id','priority_id','EXECUTION_READY'),
 ('OPERATING_COMMAND','execution_queues','execution_queue_id','execution_queue_result','EXECUTION_READY','operating_commands','command_id','execution_queue_id','COMMAND_READY'),
 ('BUSINESS_OPERATING_STATE','operating_commands','command_id','command_result','COMMAND_READY','business_operating_states','operating_state_id','command_id','OPERATING_READY'),
)

class OperatingCommandChainService(AuthoritativeService):
 service_name='operating_command_chain_service'
 def __init__(self,path):
  self.path=Path(path); self.database=DatabaseManager(self.path); self.database.initialize(); self.events=EventRepository(); super().__init__(self.database,self.events)
  with self.database.transaction() as c:
   for event_type,_,_,_,_,table,idcol,parent_table,parentcol,result in STAGES:
    hist=f'{table}_history'; resultcol=self._result_col(table); requestcol=self._request_col(table); eventcol=self._event_col(table)
    c.executescript(f'''CREATE TABLE IF NOT EXISTS {table}({idcol} TEXT PRIMARY KEY,{parentcol} TEXT NOT NULL UNIQUE,{requestcol} TEXT NOT NULL UNIQUE,{eventcol} TEXT NOT NULL UNIQUE,authority_code TEXT NOT NULL,authority_reason TEXT NOT NULL,{resultcol} TEXT NOT NULL CHECK({resultcol}='{result}'),created_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS {hist}(history_id INTEGER PRIMARY KEY AUTOINCREMENT,{idcol} TEXT NOT NULL,{parentcol} TEXT NOT NULL,{eventcol} TEXT NOT NULL,authority_code TEXT NOT NULL,{resultcol} TEXT NOT NULL CHECK({resultcol}='{result}'),recorded_at TEXT NOT NULL,UNIQUE({eventcol},{resultcol})); CREATE TRIGGER IF NOT EXISTS {table}_no_update BEFORE UPDATE ON {table} BEGIN SELECT RAISE(ABORT,'{table} is append-only'); END; CREATE TRIGGER IF NOT EXISTS {table}_no_delete BEFORE DELETE ON {table} BEGIN SELECT RAISE(ABORT,'{table} is append-only'); END; CREATE TRIGGER IF NOT EXISTS {hist}_no_update BEFORE UPDATE ON {hist} BEGIN SELECT RAISE(ABORT,'{hist} is append-only'); END; CREATE TRIGGER IF NOT EXISTS {hist}_no_delete BEFORE DELETE ON {hist} BEGIN SELECT RAISE(ABORT,'{hist} is append-only'); END;''')
 def _result_col(self,t): return {'action_plans':'action_plan_result','business_priorities':'priority_result','execution_queues':'execution_queue_result','operating_commands':'command_result','business_operating_states':'operating_state_result'}[t]
 def _request_col(self,t): return {'action_plans':'action_plan_request_id','business_priorities':'priority_request_id','execution_queues':'execution_queue_request_id','operating_commands':'command_request_id','business_operating_states':'operating_state_request_id'}[t]
 def _event_col(self,t): return {'action_plans':'action_plan_event_id','business_priorities':'priority_event_id','execution_queues':'execution_queue_event_id','operating_commands':'command_event_id','business_operating_states':'operating_state_event_id'}[t]
 def reconstruct(self,*,stage,authority_id,parent_id,request_id,intent):
  stage=str(stage).upper(); spec=next((x for x in STAGES if x[0]==stage),None)
  if not spec or not all(str(v).strip() for v in (authority_id,parent_id,request_id)) or str(intent).upper()!=f'RECONSTRUCT_{stage}': raise OperatingChainBlocked('Explicit complete operating authority required')
  event_type,parent_table,parent_idcol,parent_resultcol,parent_result,table,idcol,parentcol,result=spec; resultcol=self._result_col(table); requestcol=self._request_col(table); eventcol=self._event_col(table); payload={'authority_id':authority_id,'parent_id':parent_id,'stage':stage}; event=self._new_event(event_type,request_id,payload)
  with self.database.read_connection() as c:
   prior=c.execute('SELECT * FROM event_identity WHERE request_id=?',(request_id,)).fetchone()
   if prior:
    row=c.execute(f'SELECT * FROM {table} WHERE {requestcol}=?',(request_id,)).fetchone()
    if row and row[idcol]==authority_id and prior['payload_sha256']==event.payload_sha256: self._replay(prior,event_type); return self.get(stage,authority_id)
    raise OperatingChainBlocked(f'{stage} request identity mismatch')
  with self.database.transaction() as c:
   parent=c.execute(f'SELECT * FROM {parent_table} WHERE {parent_idcol}=? AND {parent_resultcol}=?',(parent_id,parent_result)).fetchone()
   if not parent: raise OperatingChainBlocked(f'Accepted {parent_result} authority required')
   if c.execute(f'SELECT 1 FROM {table} WHERE {parentcol}=?',(parent_id,)).fetchone(): raise OperatingChainBlocked(f'Second {stage} authority blocked')
   code,reason=self._derive(stage,parent)
   preserved=('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_ledger_postings','business_ledger_balances','business_performance_summaries','business_performance_intelligence','business_decisions'); before=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in preserved); sold=c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n']
   self._append_event_and_audit(c,event,f'reconstruct_{stage.lower()}'); c.execute(f'INSERT INTO {table}({idcol},{parentcol},{requestcol},{eventcol},authority_code,authority_reason,{resultcol},created_at) VALUES (?,?,?,?,?,?,?,?)',(authority_id,parent_id,request_id,event.event_id,code,reason,result,event.committed_at)); c.execute(f'INSERT INTO {table}_history({idcol},{parentcol},{eventcol},authority_code,{resultcol},recorded_at) VALUES (?,?,?,?,?,?)',(authority_id,parent_id,event.event_id,code,result,event.committed_at)); c.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)',(event.event_id,event_type,authority_id,'VERIFIED',event.committed_at)); self._verify_event(c,event)
   after=tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in preserved)
   if before!=after or sold!=c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n']: raise RuntimeError(f'{stage} mutated preserved authority')
  return self.get(stage,authority_id)
 def _derive(self,stage,parent):
  if stage=='ACTION_PLAN':
   code='EXPAND_PROFITABLE_CHANNEL'; reason=f"Translate {parent['decision_code']} into controlled profitable-channel expansion"
  elif stage=='BUSINESS_PRIORITY': code='PRIORITY_1_PROFITABLE_CHANNEL'; reason='Rank profitable-channel expansion as highest business priority'
  elif stage=='EXECUTION_QUEUE': code='QUEUE_PROFITABLE_CHANNEL_EXPANSION'; reason='Queue highest-ranked profitable-channel work for controlled execution'
  elif stage=='OPERATING_COMMAND': code='EXECUTE_CONTROLLED_CHANNEL_EXPANSION'; reason='Authorize execution-ready profitable-channel work within preserved authority boundaries'
  else: code='OPERATE_CONTROLLED_GROWTH'; reason='Declare current operating state ready for controlled profitable growth'
  return code,reason
 def _replay(self,prior,event_type):
  with self.database.transaction() as c: c.execute("INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES (?,?,?,?, 'BLOCKED',?)",(prior['request_id'],prior['event_id'],event_type,prior['payload_sha256'],prior['committed_at']))
 def get(self,stage,authority_id):
  spec=next(x for x in STAGES if x[0]==str(stage).upper()); table=spec[5]; idcol=spec[6]; hist=f'{table}_history'
  with self.database.read_connection() as c:
   row=c.execute(f'SELECT * FROM {table} WHERE {idcol}=?',(authority_id,)).fetchone(); h=c.execute(f'SELECT COUNT(*) n FROM {hist} WHERE {idcol}=?',(authority_id,)).fetchone()['n']
   if not row or h!=1: raise OperatingChainBlocked(f'{stage} reconstruction failed')
   return dict(row)
