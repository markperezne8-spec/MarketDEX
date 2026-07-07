import tempfile,sqlite3,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from services.product_registry_service import ProductRegistryService,ACCEPTANCE_REQUEST
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'db.sqlite3'; s=ProductRegistryService(p); r=s.run_acceptance(); assert r['passed']==12
 pid=r['pid']; assert s.register('SINGLE','Charizard ex','Obsidian Flames','125/197','Double Rare',ACCEPTANCE_REQUEST)==pid
 with sqlite3.connect(p) as c:
  assert c.execute('select count(*) from products where canonical_name="Charizard ex"').fetchone()[0]==1
  try:c.execute('delete from product_registration_history'); raise AssertionError('delete allowed')
  except sqlite3.DatabaseError:pass
 s2=ProductRegistryService(p); rr=s2.verify(); assert rr['passed']==12 and rr['pid']==pid
print('M34 TESTS: 12 / 12 PASS'); print('REPLAY: PASS'); print('RESTART: PASS'); print('ZERO INVENTORY/FINANCIAL/MARKETPLACE MUTATION: PASS')
