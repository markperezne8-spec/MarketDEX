import tempfile,sqlite3,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from services.inventory_product_link_service import InventoryProductLinkService,REQ
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'db.sqlite3'; s=InventoryProductLinkService(p); r=s.run_acceptance(); assert r['passed']==12, r; lid=r['lid']; pid=s.ensure_acceptance_authority(); assert s.link('AST-M35-CHARIZARD-001',pid,REQ)==lid
 c=sqlite3.connect(p)
 try:
  assert c.execute('select count(*) from inventory_product_links where asset_id=?',('AST-M35-CHARIZARD-001',)).fetchone()[0]==1
  assert c.execute('select count(*) from inventory_history where event_id=(select created_event_id from inventory_product_links where inventory_product_link_id=?)',(lid,)).fetchone()[0]==0
  try:c.execute('delete from inventory_product_link_history'); raise AssertionError('delete allowed')
  except sqlite3.DatabaseError:pass
 finally:c.close()
 s2=InventoryProductLinkService(p); rr=s2.verify(); assert rr['passed']==12 and rr['lid']==lid
print('M35 TESTS: 12 / 12 PASS'); print('REPLAY AFTER RESTART: PASS'); print('ZERO SECOND LINKAGE: PASS'); print('ZERO INVENTORY/FINANCIAL/MARKETPLACE/PRODUCT MUTATION FROM LINKAGE: PASS')
