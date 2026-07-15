import sqlite3, tempfile, unittest
from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_identity import EventIdentity
from core.event_repository import EventRepository, ReplayRejected

class AuthorityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.db = DatabaseManager(Path(self.tmp.name)/'test.sqlite3'); self.db.initialize(); self.repo=EventRepository()
    def tearDown(self): self.tmp.cleanup()
    def test_replay_rejected(self):
        with self.db.transaction() as c: self.repo.append(c, EventIdentity.create('ACQUISITION','REQ-1',{'q':1}))
        with self.assertRaises(ReplayRejected):
            with self.db.transaction() as c: self.repo.append(c, EventIdentity.create('ACQUISITION','REQ-1',{'q':1}))
        with self.db.read_connection() as c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM event_identity').fetchone()[0], 1)
    def test_event_immutable(self):
        with self.db.transaction() as c: self.repo.append(c, EventIdentity.create('MOVEMENT','REQ-2',{}))
        with self.assertRaises(sqlite3.IntegrityError):
            with self.db.transaction() as c: c.execute("UPDATE event_identity SET event_type='X'")
    def test_audit_append_only(self):
        from repositories.asset_repository import AssetRepository
        from services.asset_service import AssetService
        AssetService(self.db, self.repo, AssetRepository()).create_asset(
            request_id='REQ-3',
            asset_id='ASSET-3',
            asset_name='Foundation probe',
            asset_type='TEST',
        )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.db.transaction() as c: c.execute('DELETE FROM audit_history')
