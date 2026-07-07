import sqlite3
import pytest
from services.m40a_acceptance_service import M40AAcceptanceService,FINALIZATION_ID,FINALIZATION_REQUEST_ID
from services.m39b_acceptance_service import M39BAcceptanceService,CLOSURE_ID
from services.m39a_acceptance_service import SETTLEMENT_ID
from services.product_sale_execution_service import SALE_ID
from services.financial_finalization_service import FinancialFinalizationService,FinancialFinalizationBlocked

def fixture(path):
 assert M39BAcceptanceService(path).execute()['passed']==12
 svc=FinancialFinalizationService(path); k=dict(finalization_id=FINALIZATION_ID,closure_id=CLOSURE_ID,sale_id=SALE_ID,settlement_id=SETTLEMENT_ID,finalization_request_id=FINALIZATION_REQUEST_ID,intent='FINALIZE'); return svc,k

def test_m40a_exact_acceptance_12_of_12(tmp_path):
 r=M40AAcceptanceService(tmp_path/'m40a.sqlite3').execute(); assert r['passed']==12; assert r['result']=='CLOSED ORDER FINANCIAL FINALIZATION VERIFIED'

def test_replay_restart_exactly_once(tmp_path):
 path=tmp_path/'replay.sqlite3'; svc,k=fixture(path); a=svc.finalize(**k); b=svc.finalize(**k); d=FinancialFinalizationService(path).finalize(**k); assert a['finalization_event_id']==b['finalization_event_id']==d['finalization_event_id']
 with svc.database.read_connection() as c: assert c.execute('SELECT COUNT(*) n FROM financial_finalizations').fetchone()['n']==1; assert c.execute('SELECT COUNT(*) n FROM financial_finalization_history').fetchone()['n']==1

def test_closed_lineage_and_second_finalization_fail_closed(tmp_path):
 svc,k=fixture(tmp_path/'blocked.sqlite3')
 with pytest.raises(FinancialFinalizationBlocked): svc.finalize(**dict(k,closure_id='UNKNOWN'))
 svc.finalize(**k)
 with pytest.raises(FinancialFinalizationBlocked): svc.finalize(**dict(k,finalization_id='FINALIZATION-SECOND',finalization_request_id='M40A-SECOND'))

def test_zero_upstream_mutation(tmp_path):
 svc,k=fixture(tmp_path/'zero.sqlite3')
 def counts(c): return (c.execute('SELECT COUNT(*) n FROM sales').fetchone()['n'],c.execute('SELECT COUNT(*) n FROM sales_financial_history').fetchone()['n'],c.execute('SELECT COUNT(*) n FROM settlement_executions').fetchone()['n'],c.execute('SELECT COUNT(*) n FROM order_closures').fetchone()['n'],c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n'])
 with svc.database.read_connection() as c: before=counts(c)
 svc.finalize(**k)
 with svc.database.read_connection() as c: after=counts(c)
 assert before==after

def test_finalization_history_append_only(tmp_path):
 svc,k=fixture(tmp_path/'append.sqlite3'); svc.finalize(**k)
 with pytest.raises(sqlite3.IntegrityError):
  with svc.database.transaction() as c: c.execute('DELETE FROM financial_finalization_history WHERE finalization_id=?',(FINALIZATION_ID,))
