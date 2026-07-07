import sqlite3
import pytest
from services.m42a_acceptance_service import M42AAcceptanceService,SUMMARY_ID,SUMMARY_REQUEST_ID
from services.m41b_acceptance_service import M41BAcceptanceService,BALANCE_ID
from services.business_performance_summary_service import BusinessPerformanceSummaryService,BusinessPerformanceSummaryBlocked

def fixture(path):
 assert M41BAcceptanceService(path).execute()['passed']==12
 return BusinessPerformanceSummaryService(path),dict(summary_id=SUMMARY_ID,balance_id=BALANCE_ID,summary_request_id=SUMMARY_REQUEST_ID,intent='SUMMARIZE')
def test_m42a_exact_acceptance_12_of_12(tmp_path):
 r=M42AAcceptanceService(tmp_path/'m42a.sqlite3').execute(); assert r['passed']==12; assert r['result']=='BUSINESS PERFORMANCE SUMMARY AUTHORITY VERIFIED'; assert r['sale_count']==1; assert r['profit']==4200
def test_replay_restart_exactly_once(tmp_path):
 path=tmp_path/'replay.sqlite3'; svc,k=fixture(path); a=svc.summarize(**k); b=svc.summarize(**k); d=BusinessPerformanceSummaryService(path).summarize(**k); assert a['summary_event_id']==b['summary_event_id']==d['summary_event_id']
 with svc.database.read_connection() as c: assert c.execute('SELECT COUNT(*) n FROM business_performance_summaries').fetchone()['n']==1; assert c.execute('SELECT COUNT(*) n FROM business_performance_summary_history').fetchone()['n']==1
def test_balanced_lineage_and_second_summary_fail_closed(tmp_path):
 svc,k=fixture(tmp_path/'blocked.sqlite3')
 with pytest.raises(BusinessPerformanceSummaryBlocked): svc.summarize(**dict(k,balance_id='UNKNOWN'))
 svc.summarize(**k)
 with pytest.raises(BusinessPerformanceSummaryBlocked): svc.summarize(**dict(k,summary_id='SUMMARY-SECOND',summary_request_id='M42A-SECOND'))
def test_zero_upstream_mutation(tmp_path):
 svc,k=fixture(tmp_path/'zero.sqlite3'); tables=('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_ledger_postings','business_ledger_balances')
 def counts(c): return tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables)
 with svc.database.read_connection() as c: before=counts(c)
 svc.summarize(**k)
 with svc.database.read_connection() as c: after=counts(c)
 assert before==after
def test_summary_history_append_only(tmp_path):
 svc,k=fixture(tmp_path/'append.sqlite3'); svc.summarize(**k)
 with pytest.raises(sqlite3.IntegrityError):
  with svc.database.transaction() as c: c.execute('DELETE FROM business_performance_summary_history WHERE summary_id=?',(SUMMARY_ID,))
