import tempfile, unittest
from pathlib import Path
from core.database_manager import DatabaseManager
from services.service_registry import ServiceRegistry

class M27MissionControlTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/'m.sqlite3'
        self.db=DatabaseManager(self.path)
        self.db.initialize()
        self.s=ServiceRegistry(self.db)
        self.s.asset.create_asset(request_id='a',asset_id='PACK',asset_name='Pack',asset_type='PACK',state='COMPLETED')
        self.s.inventory.apply_acquisition(request_id='i',asset_id='PACK',quantity=6,total_cost_minor=6000)
        self.s.sales.record_sale(request_id='sale',sale_id='S1',asset_id='PACK',quantity=2,revenue_minor=3000,marketplace_fees_minor=300,shipping_minor=500,packaging_minor=100)
        with self.db.connect() as c:
            self.sale_event=c.execute("SELECT created_event_id FROM sales WHERE sale_id='S1'").fetchone()[0]

    def tearDown(self):
        self.tmp.cleanup()

    def test_dashboard_derives_existing_authority(self):
        m=self.s.dashboard.mission_control()
        self.assertEqual(m['units_on_hand'],4)
        self.assertEqual(m['inventory_cost_minor'],4000)
        self.assertEqual(m['completed_sales'],1)
        self.assertEqual(m['revenue_minor'],3000)
        self.assertEqual(m['realized_profit_minor'],100)
        self.assertEqual(m['authoritative_events'],3)

    def test_return_restatement_is_derived(self):
        self.s.return_service.execute(request_id='ret',return_id='R1',sale_id='S1',quantity=2,condition_evidence='SEALED VERIFIED',restock_authorized=True,refund_minor=3000)
        m=self.s.dashboard.mission_control()
        self.assertEqual(m['units_on_hand'],6)
        self.assertEqual(m['inventory_cost_minor'],6000)
        self.assertEqual(m['realized_profit_minor'],-900)
        self.assertEqual(m['returns'],1)

    def test_exception_and_audit_are_derived(self):
        self.s.exception.record(request_id='ex',exception_id='E1',exception_type='AUTHORITY_REVIEW',evidence='evidence',source_event_id=self.sale_event)
        self.s.audit.verify(request_id='au',audit_verification_id='AU1',target_event_id=self.sale_event)
        m=self.s.dashboard.mission_control()
        self.assertEqual(m['review_exceptions'],1)
        self.assertEqual((m['verified_audits'],m['audit_count']),(1,1))

    def test_dashboard_is_read_only_zero_truth_writes(self):
        with self.db.connect() as c:
            before=(c.execute('SELECT COUNT(*) FROM event_identity').fetchone()[0],
                    c.execute('SELECT COUNT(*) FROM audit_history').fetchone()[0])
        self.s.dashboard.mission_control()
        self.s.dashboard.recent_authority()
        self.s.dashboard.mission_control()
        with self.db.connect() as c:
            after=(c.execute('SELECT COUNT(*) FROM event_identity').fetchone()[0],
                   c.execute('SELECT COUNT(*) FROM audit_history').fetchone()[0])
        self.assertEqual(before,after)

    def test_recent_authority_is_permanent_event_history(self):
        rows=self.s.dashboard.recent_authority()
        self.assertEqual(len(rows),3)
        self.assertEqual(rows[0]['event_type'],'SALE')

    def test_restart_rederives_same_truth(self):
        before=self.s.dashboard.mission_control()
        db2=DatabaseManager(self.path); db2.initialize()
        after=ServiceRegistry(db2).dashboard.mission_control()
        self.assertEqual(before,after)

if __name__=='__main__':
    unittest.main()
