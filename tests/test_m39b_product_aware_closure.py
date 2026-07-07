import sqlite3
import pytest
from services.m39b_acceptance_service import M39BAcceptanceService,CLOSURE_ID,CLOSURE_REQUEST_ID
from services.m39a_acceptance_service import M39AAcceptanceService,SETTLEMENT_ID
from services.product_sale_execution_service import SALE_ID
from services.order_closure_service import OrderClosureService,OrderClosureBlocked

def fixture(path):
 assert M39AAcceptanceService(path).execute()['passed']==12
 svc=OrderClosureService(path)
 with svc.database.read_connection() as c:
  sale=c.execute('SELECT * FROM sales WHERE sale_id=?',(SALE_ID,)).fetchone(); sold=c.execute("SELECT * FROM publication_lifecycle_events WHERE sale_id=? AND event_type='SOLD_CONVERSION'",(SALE_ID,)).fetchone(); alloc=c.execute('SELECT * FROM marketplace_publication_allocations WHERE allocation_id=?',(sold['allocation_id'],)).fetchone(); listing=c.execute('SELECT * FROM marketplace_listing_identities WHERE listing_identity_id=?',(alloc['publication_identity'],)).fetchone()
 return svc,dict(closure_id=CLOSURE_ID,sale_id=SALE_ID,settlement_id=SETTLEMENT_ID,product_id=listing['product_id'],asset_id=sale['asset_id'],listing_id=listing['listing_identity_id'],allocation_id=alloc['allocation_id'],marketplace='eBay',closure_request_id=CLOSURE_REQUEST_ID,intent='CLOSE')

def test_m39b_exact_acceptance_12_of_12(tmp_path):
 r=M39BAcceptanceService(tmp_path/'m39b.sqlite3').execute(); assert r['passed']==12; assert r['result']=='PRODUCT-AWARE SETTLEMENT + ORDER CLOSURE VERIFIED'

def test_closure_replay_restart_exactly_once(tmp_path):
 path=tmp_path/'replay.sqlite3'; svc,k=fixture(path); a=svc.close(**k); b=svc.close(**k); d=OrderClosureService(path).close(**k); assert a['closure_event_id']==b['closure_event_id']==d['closure_event_id']
 with svc.database.read_connection() as c: assert c.execute('SELECT COUNT(*) n FROM order_closures').fetchone()['n']==1; assert c.execute('SELECT COUNT(*) n FROM order_closure_history').fetchone()['n']==1

def test_lineage_mismatch_and_second_closure_fail_closed(tmp_path):
 svc,k=fixture(tmp_path/'blocked.sqlite3')
 with pytest.raises(OrderClosureBlocked): svc.close(**dict(k,marketplace='TCGplayer'))
 svc.close(**k)
 with pytest.raises(OrderClosureBlocked): svc.close(**dict(k,closure_id='CLOSURE-SECOND',closure_request_id='M39B-SECOND-CLOSE'))

def test_zero_preserved_authority_mutation(tmp_path):
 svc,k=fixture(tmp_path/'zero.sqlite3')
 with svc.database.read_connection() as c: before=(c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=?',(k['asset_id'],)).fetchone()['quantity'],c.execute('SELECT COUNT(*) n FROM sales').fetchone()['n'],c.execute('SELECT COUNT(*) n FROM sales_financial_history').fetchone()['n'],c.execute('SELECT COUNT(*) n FROM settlement_executions').fetchone()['n'],c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n'])
 svc.close(**k)
 with svc.database.read_connection() as c: after=(c.execute('SELECT quantity FROM inventory_authority WHERE asset_id=?',(k['asset_id'],)).fetchone()['quantity'],c.execute('SELECT COUNT(*) n FROM sales').fetchone()['n'],c.execute('SELECT COUNT(*) n FROM sales_financial_history').fetchone()['n'],c.execute('SELECT COUNT(*) n FROM settlement_executions').fetchone()['n'],c.execute("SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'").fetchone()['n'])
 assert before==after

def test_closure_history_append_only(tmp_path):
 svc,k=fixture(tmp_path/'append.sqlite3'); svc.close(**k)
 with pytest.raises(sqlite3.IntegrityError):
  with svc.database.transaction() as c: c.execute('DELETE FROM order_closure_history WHERE closure_id=?',(CLOSURE_ID,))
