import sqlite3
import pytest
from services.m41b_acceptance_service import M41BAcceptanceService,BALANCE_ID,BALANCE_REQUEST_ID
from services.m41a_acceptance_service import M41AAcceptanceService,POSTING_ID,LEDGER_ACCOUNT
from services.business_ledger_balance_service import BusinessLedgerBalanceService,BusinessLedgerBalanceBlocked

def fixture(path):
 assert M41AAcceptanceService(path).execute()['passed']==12
 return BusinessLedgerBalanceService(path),dict(balance_id=BALANCE_ID,posting_id=POSTING_ID,balance_request_id=BALANCE_REQUEST_ID,ledger_account=LEDGER_ACCOUNT,intent='BALANCE')
def test_m41b_exact_acceptance_12_of_12(tmp_path):
 r=M41BAcceptanceService(tmp_path/'m41b.sqlite3').execute(); assert r['passed']==12; assert r['result']=='BUSINESS LEDGER BALANCE AUTHORITY VERIFIED'
def test_replay_restart_exactly_once(tmp_path):
 path=tmp_path/'replay.sqlite3'; svc,k=fixture(path); a=svc.balance(**k); b=svc.balance(**k); d=BusinessLedgerBalanceService(path).balance(**k); assert a['balance_event_id']==b['balance_event_id']==d['balance_event_id']
 with svc.database.read_connection() as c: assert c.execute('SELECT COUNT(*) n FROM business_ledger_balances').fetchone()['n']==1; assert c.execute('SELECT COUNT(*) n FROM business_ledger_balance_history').fetchone()['n']==1
def test_posted_lineage_and_second_balance_fail_closed(tmp_path):
 svc,k=fixture(tmp_path/'blocked.sqlite3')
 with pytest.raises(BusinessLedgerBalanceBlocked): svc.balance(**dict(k,posting_id='UNKNOWN'))
 svc.balance(**k)
 with pytest.raises(BusinessLedgerBalanceBlocked): svc.balance(**dict(k,balance_id='BALANCE-SECOND',balance_request_id='M41B-SECOND'))
def test_zero_upstream_mutation(tmp_path):
 svc,k=fixture(tmp_path/'zero.sqlite3')
 tables=('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations','profit_recognitions','business_ledger_postings')
 def counts(c): return tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in tables)
 with svc.database.read_connection() as c: before=counts(c)
 svc.balance(**k)
 with svc.database.read_connection() as c: after=counts(c)
 assert before==after
def test_balance_history_append_only(tmp_path):
 svc,k=fixture(tmp_path/'append.sqlite3'); svc.balance(**k)
 with pytest.raises(sqlite3.IntegrityError):
  with svc.database.transaction() as c: c.execute('DELETE FROM business_ledger_balance_history WHERE balance_id=?',(BALANCE_ID,))
