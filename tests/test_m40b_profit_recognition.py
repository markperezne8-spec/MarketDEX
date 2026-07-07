import sqlite3
import pytest
from services.m40b_acceptance_service import M40BAcceptanceService,RECOGNITION_ID,RECOGNITION_REQUEST_ID
from services.m40a_acceptance_service import M40AAcceptanceService,FINALIZATION_ID
from services.product_sale_execution_service import SALE_ID
from services.profit_recognition_service import ProfitRecognitionService,ProfitRecognitionBlocked

def fixture(path):
 assert M40AAcceptanceService(path).execute()['passed']==12
 return ProfitRecognitionService(path),dict(recognition_id=RECOGNITION_ID,finalization_id=FINALIZATION_ID,sale_id=SALE_ID,recognition_request_id=RECOGNITION_REQUEST_ID,intent='RECOGNIZE')
def test_m40b_exact_acceptance_12_of_12(tmp_path):
 r=M40BAcceptanceService(tmp_path/'m40b.sqlite3').execute(); assert r['passed']==12; assert r['result']=='FINALIZED SALE PROFIT RECOGNITION VERIFIED'
def test_replay_restart_exactly_once(tmp_path):
 path=tmp_path/'replay.sqlite3'; svc,k=fixture(path); a=svc.recognize(**k); b=svc.recognize(**k); d=ProfitRecognitionService(path).recognize(**k); assert a['recognition_event_id']==b['recognition_event_id']==d['recognition_event_id']
 with svc.database.read_connection() as c: assert c.execute('SELECT COUNT(*) n FROM profit_recognitions').fetchone()['n']==1; assert c.execute('SELECT COUNT(*) n FROM profit_recognition_history').fetchone()['n']==1
def test_finalized_lineage_and_second_recognition_fail_closed(tmp_path):
 svc,k=fixture(tmp_path/'blocked.sqlite3')
 with pytest.raises(ProfitRecognitionBlocked): svc.recognize(**dict(k,finalization_id='UNKNOWN'))
 svc.recognize(**k)
 with pytest.raises(ProfitRecognitionBlocked): svc.recognize(**dict(k,recognition_id='RECOGNITION-SECOND',recognition_request_id='M40B-SECOND'))
def test_zero_upstream_mutation(tmp_path):
 svc,k=fixture(tmp_path/'zero.sqlite3')
 def counts(c): return tuple(c.execute(f'SELECT COUNT(*) n FROM {t}').fetchone()['n'] for t in ('sales','sales_financial_history','settlement_executions','order_closures','financial_finalizations'))
 with svc.database.read_connection() as c: before=counts(c)
 svc.recognize(**k)
 with svc.database.read_connection() as c: after=counts(c)
 assert before==after
def test_recognition_history_append_only(tmp_path):
 svc,k=fixture(tmp_path/'append.sqlite3'); svc.recognize(**k)
 with pytest.raises(sqlite3.IntegrityError):
  with svc.database.transaction() as c: c.execute('DELETE FROM profit_recognition_history WHERE recognition_id=?',(RECOGNITION_ID,))
