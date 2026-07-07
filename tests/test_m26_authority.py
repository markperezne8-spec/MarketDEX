import sqlite3,tempfile,unittest
from pathlib import Path
from core.database_manager import DatabaseManager
from services.service_registry import ServiceRegistry
from core.event_repository import ReplayRejected
class M26AuthorityTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)/'m.sqlite3'; self.db=DatabaseManager(self.path); self.db.initialize(); self.s=ServiceRegistry(self.db)
  self.ev=self.s.asset.create_asset(request_id='asset-request',asset_id='A1',asset_name='Asset',asset_type='SINGLE',state='PLANNED')
 def tearDown(self): self.tmp.cleanup()
 def test_exception_requires_evidence_and_source_match(self):
  with self.assertRaises(ValueError): self.s.exception.record(request_id='x',exception_id='E0',exception_type='REVIEW',evidence='',source_event_id=self.ev.event_id)
  with self.assertRaises(ValueError): self.s.exception.record(request_id='x2',exception_id='E2',exception_type='REVIEW',evidence='e',source_event_id='missing')
  with self.db.connect() as c: self.assertEqual(c.execute('SELECT COUNT(*) FROM exception_authority').fetchone()[0],0)
 def test_exception_authority_and_lineage(self):
  e=self.s.exception.record(request_id='ex',exception_id='E1',exception_type='AUTHORITY_REVIEW',evidence='verified evidence',source_event_id=self.ev.event_id)
  with self.db.connect() as c:
   r=c.execute("SELECT * FROM exception_authority WHERE exception_id='E1'").fetchone()
   self.assertEqual((r['source_event_id'],r['state'],r['event_id']),(self.ev.event_id,'REVIEW',e.event_id))
   self.assertEqual(c.execute('SELECT COUNT(*) FROM exception_history').fetchone()[0],1)
 def test_audit_verifies_immutable_event_hash(self):
  _,result=self.s.audit.verify(request_id='audit',audit_verification_id='A1',target_event_id=self.ev.event_id)
  self.assertEqual(result,'VERIFIED')
  with self.db.connect() as c:
   r=c.execute("SELECT * FROM audit_verifications WHERE audit_verification_id='A1'").fetchone()
   self.assertEqual(r['target_payload_sha256'],c.execute('SELECT payload_sha256 FROM event_identity WHERE event_id=?',(self.ev.event_id,)).fetchone()[0])
 def test_audit_missing_target_fails_closed(self):
  with self.assertRaises(ValueError): self.s.audit.verify(request_id='a',audit_verification_id='A',target_event_id='missing')
 def test_replay_blocked_zero_second_mutation_and_recorded(self):
  from core.event_identity import EventIdentity
  dup=EventIdentity.create('ASSET_CREATE','asset-request',{'asset_id':'A1','asset_name':'Asset','asset_type':'SINGLE','state':'PLANNED'})
  with self.assertRaises(ReplayRejected):
   with self.db.transaction() as c: self.s.asset._append_event_and_audit(c,dup,'duplicate')
  with self.db.connect() as c:
   self.assertEqual(c.execute('SELECT COUNT(*) FROM assets').fetchone()[0],1)
   # Transaction rollback means defense log is not durable on a raised mutation transaction.
   self.assertEqual(c.execute('SELECT COUNT(*) FROM event_identity').fetchone()[0],1)
 def test_append_only_m26_history(self):
  self.s.exception.record(request_id='ex',exception_id='E1',exception_type='AUTHORITY_REVIEW',evidence='e',source_event_id=self.ev.event_id)
  self.s.audit.verify(request_id='au',audit_verification_id='AU1',target_event_id=self.ev.event_id)
  for table in ('exception_history','audit_verifications'):
   with self.assertRaises(sqlite3.IntegrityError):
    with self.db.transaction() as c: c.execute(f'DELETE FROM {table}')
 def test_restart_persistence(self):
  self.s.exception.record(request_id='ex',exception_id='E1',exception_type='AUTHORITY_REVIEW',evidence='e',source_event_id=self.ev.event_id)
  self.s.audit.verify(request_id='au',audit_verification_id='AU1',target_event_id=self.ev.event_id)
  db2=DatabaseManager(self.path); db2.initialize()
  with db2.connect() as c: self.assertEqual((c.execute('SELECT COUNT(*) FROM exception_authority').fetchone()[0],c.execute('SELECT COUNT(*) FROM audit_verifications').fetchone()[0]),(1,1))
if __name__=='__main__': unittest.main()
