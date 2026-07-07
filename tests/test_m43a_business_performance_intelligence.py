import sqlite3
import pytest
from services.m43a_acceptance_service import M43AAcceptanceService,INTELLIGENCE_ID,INTELLIGENCE_REQUEST_ID
from services.m42a_acceptance_service import M42AAcceptanceService,SUMMARY_ID
from services.business_performance_intelligence_service import BusinessPerformanceIntelligenceService,BusinessPerformanceIntelligenceBlocked

def fixture(path):
 assert M42AAcceptanceService(path).execute()['passed']==12
 return BusinessPerformanceIntelligenceService(path),dict(intelligence_id=INTELLIGENCE_ID,summary_id=SUMMARY_ID,intelligence_request_id=INTELLIGENCE_REQUEST_ID,intent='RECONSTRUCT_INTELLIGENCE')
def test_m43a_exact_acceptance_12_of_12(tmp_path):
 r=M43AAcceptanceService(tmp_path/'m43a.sqlite3').execute(); assert r['passed']==12; assert r['result']=='BUSINESS PERFORMANCE INTELLIGENCE AUTHORITY VERIFIED'; assert r['margin']==8400; assert r['status']=='PROFITABLE'
def test_replay_restart_exactly_once(tmp_path):
 path=tmp_path/'replay.sqlite3'; svc,k=fixture(path); a=svc.reconstruct(**k); b=svc.reconstruct(**k); d=BusinessPerformanceIntelligenceService(path).reconstruct(**k); assert a['intelligence_event_id']==b['intelligence_event_id']==d['intelligence_event_id']
 with svc.database.read_connection() as c: assert c.execute('SELECT COUNT(*) n FROM business_performance_intelligence').fetchone()['n']==1; assert c.execute('SELECT COUNT(*) n FROM business_performance_intelligence_history').fetchone()['n']==1
def test_summary_lineage_and_second_intelligence_fail_closed(tmp_path):
 svc,k=fixture(tmp_path/'blocked.sqlite3')
 with pytest.raises(BusinessPerformanceIntelligenceBlocked): svc.reconstruct(**dict(k,summary_id='UNKNOWN'))
 svc.reconstruct(**k)
 with pytest.raises(BusinessPerformanceIntelligenceBlocked): svc.reconstruct(**dict(k,intelligence_id='INTELLIGENCE-SECOND',intelligence_request_id='M43A-SECOND'))
def test_zero_upstream_mutation(tmp_path):
 svc,k=fixture(tmp_path/'zero.sqlite3'); tables=('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_ledger_postings','business_ledger_balances','business_performance_summaries')
 def counts(c): return tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables)
 with svc.database.read_connection() as c: before=counts(c)
 svc.reconstruct(**k)
 with svc.database.read_connection() as c: after=counts(c)
 assert before==after
def test_intelligence_history_append_only(tmp_path):
 svc,k=fixture(tmp_path/'append.sqlite3'); svc.reconstruct(**k)
 with pytest.raises(sqlite3.IntegrityError):
  with svc.database.transaction() as c: c.execute('DELETE FROM business_performance_intelligence_history WHERE intelligence_id=?',(INTELLIGENCE_ID,))
