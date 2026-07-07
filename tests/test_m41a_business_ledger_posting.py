import sqlite3
import pytest
from services.m41a_acceptance_service import M41AAcceptanceService,POSTING_ID,POSTING_REQUEST_ID,LEDGER_ACCOUNT
from services.m40b_acceptance_service import M40BAcceptanceService,RECOGNITION_ID
from services.product_sale_execution_service import SALE_ID
from services.business_ledger_posting_service import BusinessLedgerPostingService,BusinessLedgerPostingBlocked

def fixture(path):
 assert M40BAcceptanceService(path).execute()['passed']==12
 return BusinessLedgerPostingService(path),dict(posting_id=POSTING_ID,recognition_id=RECOGNITION_ID,sale_id=SALE_ID,posting_request_id=POSTING_REQUEST_ID,ledger_account=LEDGER_ACCOUNT,intent='POST')
def test_m41a_exact_acceptance_12_of_12(tmp_path):
 r=M41AAcceptanceService(tmp_path/'m41a.sqlite3').execute(); assert r['passed']==12; assert r['result']=='RECOGNIZED PROFIT BUSINESS LEDGER POSTING VERIFIED'
def test_replay_restart_exactly_once(tmp_path):
 path=tmp_path/'replay.sqlite3'; svc,k=fixture(path); a=svc.post(**k); b=svc.post(**k); d=BusinessLedgerPostingService(path).post(**k); assert a['posting_event_id']==b['posting_event_id']==d['posting_event_id']
 with svc.database.read_connection() as c: assert c.execute('SELECT COUNT(*) n FROM business_ledger_postings').fetchone()['n']==1; assert c.execute('SELECT COUNT(*) n FROM business_ledger_history').fetchone()['n']==1
def test_recognition_lineage_and_second_posting_fail_closed(tmp_path):
 svc,k=fixture(tmp_path/'blocked.sqlite3')
 with pytest.raises(BusinessLedgerPostingBlocked): svc.post(**dict(k,recognition_id='UNKNOWN'))
 svc.post(**k)
 with pytest.raises(BusinessLedgerPostingBlocked): svc.post(**dict(k,posting_id='POSTING-SECOND',posting_request_id='M41A-SECOND'))
def test_zero_upstream_mutation(tmp_path):
 svc,k=fixture(tmp_path/'zero.sqlite3')
 def counts(c): return tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in ('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions'))
 with svc.database.read_connection() as c: before=counts(c)
 svc.post(**k)
 with svc.database.read_connection() as c: after=counts(c)
 assert before==after
def test_business_ledger_history_append_only(tmp_path):
 svc,k=fixture(tmp_path/'append.sqlite3'); svc.post(**k)
 with pytest.raises(sqlite3.IntegrityError):
  with svc.database.transaction() as c: c.execute('DELETE FROM business_ledger_history WHERE posting_id=?',(POSTING_ID,))
