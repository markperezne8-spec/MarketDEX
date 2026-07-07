import tempfile,sqlite3,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from services.authority_parity_service import AuthorityParityService,WORKFLOWS
def main():
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/'marketdex.sqlite3'; s=AuthorityParityService(p); r=s.verify(); assert r['passed']==12; assert len(WORKFLOWS)==9; assert r['missing']==r['duplicate']==r['parallel']==r['unauthorized']==r['mc']==0; assert r['replay']=='PASS' and r['state']=='MIGRATION COMPLETE'; s.run()
  with sqlite3.connect(p) as c: first=c.execute('select count(*) from authority_parity_verifications').fetchone()[0]
  s.run()
  with sqlite3.connect(p) as c:
   second=c.execute('select count(*) from authority_parity_verifications').fetchone()[0]; assert first==second==9
   try: c.execute('update authority_parity_verifications set contract_result="BLOCKED"'); raise AssertionError('update allowed')
   except sqlite3.DatabaseError: pass
  s2=AuthorityParityService(p); rr=s2.verify(); assert rr['passed']==12 and rr['restart']=='PASS'
 print('M33 TESTS: 12 / 12 PASS'); print('REPLAY: PASS'); print('RESTART: PASS'); print('ZERO BUSINESS MUTATION FROM M33: PASS')
if __name__=='__main__': main()
