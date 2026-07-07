import sqlite3
import pytest
from services.m44a_acceptance_service import M44AAcceptanceService,DECISION_ID,DECISION_REQUEST_ID
from services.m43a_acceptance_service import M43AAcceptanceService,INTELLIGENCE_ID
from services.business_decision_service import BusinessDecisionService,BusinessDecisionBlocked

def fixture(path):
 assert M43AAcceptanceService(path).execute()['passed']==12
 return BusinessDecisionService(path),dict(decision_id=DECISION_ID,intelligence_id=INTELLIGENCE_ID,decision_request_id=DECISION_REQUEST_ID,intent='RECONSTRUCT_DECISION')
def test_m44a_exact_acceptance_12_of_12(tmp_path):
 r=M44AAcceptanceService(tmp_path/'m44a.sqlite3').execute(); assert r['passed']==12; assert r['result']=='BUSINESS DECISION AUTHORITY VERIFIED'; assert r['decision_code']=='SCALE_PROFITABLE_CHANNEL'
def test_replay_restart_exactly_once(tmp_path):
 path=tmp_path/'replay.sqlite3'; svc,k=fixture(path); a=svc.reconstruct(**k); b=svc.reconstruct(**k); d=BusinessDecisionService(path).reconstruct(**k); assert a['decision_event_id']==b['decision_event_id']==d['decision_event_id']
 with svc.database.read_connection() as c: assert c.execute('SELECT COUNT(*) n FROM business_decisions').fetchone()['n']==1; assert c.execute('SELECT COUNT(*) n FROM business_decision_history').fetchone()['n']==1
def test_intelligence_lineage_and_second_decision_fail_closed(tmp_path):
 svc,k=fixture(tmp_path/'blocked.sqlite3')
 with pytest.raises(BusinessDecisionBlocked): svc.reconstruct(**dict(k,intelligence_id='UNKNOWN'))
 svc.reconstruct(**k)
 with pytest.raises(BusinessDecisionBlocked): svc.reconstruct(**dict(k,decision_id='DECISION-SECOND',decision_request_id='M44A-SECOND'))
def test_zero_upstream_mutation(tmp_path):
 svc,k=fixture(tmp_path/'zero.sqlite3'); tables=('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_ledger_postings','business_ledger_balances','business_performance_summaries','business_performance_intelligence')
 def counts(c): return tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables)
 with svc.database.read_connection() as c: before=counts(c)
 svc.reconstruct(**k)
 with svc.database.read_connection() as c: after=counts(c)
 assert before==after
def test_decision_history_append_only(tmp_path):
 svc,k=fixture(tmp_path/'append.sqlite3'); svc.reconstruct(**k)
 with pytest.raises(sqlite3.IntegrityError):
  with svc.database.transaction() as c: c.execute('DELETE FROM business_decision_history WHERE decision_id=?',(DECISION_ID,))
