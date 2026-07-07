import sqlite3,tempfile,unittest
from pathlib import Path
from core.database_manager import DatabaseManager
from services.service_registry import ServiceRegistry

class SalesProfitAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.db=DatabaseManager(Path(self.tmp.name)/'m.sqlite3'); self.db.initialize(); self.s=ServiceRegistry(self.db)
        self.s.asset.create_asset(request_id='a',asset_id='PACK',asset_name='Pack',asset_type='PACK',state='COMPLETED')
        self.s.inventory.apply_acquisition(request_id='i',asset_id='PACK',quantity=6,total_cost_minor=6000)
    def tearDown(self): self.tmp.cleanup()
    def sale(self,request='sale',sale_id='S1',qty=2,revenue=3000,fees=300,shipping=500,packaging=100):
        return self.s.sales.record_sale(request_id=request,sale_id=sale_id,asset_id='PACK',quantity=qty,revenue_minor=revenue,marketplace_fees_minor=fees,shipping_minor=shipping,packaging_minor=packaging)
    def test_sale_decrements_inventory_and_derives_profit(self):
        self.sale()
        with self.db.connect() as c:
            inv=c.execute("SELECT * FROM inventory_authority WHERE asset_id='PACK'").fetchone()
            sale=c.execute("SELECT * FROM sales WHERE sale_id='S1'").fetchone()
            self.assertEqual((inv['quantity'],inv['total_cost_minor']),(4,4000))
            self.assertEqual(sale['cogs_minor'],2000)
            self.assertEqual(sale['profit_minor'],100)
    def test_zero_inventory_unsaleable(self):
        self.sale(qty=6)
        with self.assertRaises(ValueError): self.s.sales.record_sale(request_id='s2',sale_id='S2',asset_id='PACK',quantity=1,revenue_minor=1000,marketplace_fees_minor=0,shipping_minor=0,packaging_minor=0)
    def test_oversale_fails_closed(self):
        with self.assertRaises(ValueError): self.sale(qty=7)
        with self.db.connect() as c: self.assertEqual(c.execute("SELECT quantity FROM inventory_authority WHERE asset_id='PACK'").fetchone()[0],6)
    def test_negative_profit_is_preserved_as_truth(self):
        self.sale(revenue=1000,fees=300,shipping=500,packaging=300)
        with self.db.connect() as c: self.assertEqual(c.execute("SELECT profit_minor FROM sales WHERE sale_id='S1'").fetchone()[0],-2100)
    def test_replay_cannot_create_second_sale(self):
        self.sale()
        with self.assertRaises(Exception): self.s.sales.record_sale(request_id='sale',sale_id='S2',asset_id='PACK',quantity=1,revenue_minor=1000,marketplace_fees_minor=0,shipping_minor=0,packaging_minor=0)
        with self.db.connect() as c: self.assertEqual(c.execute('SELECT COUNT(*) FROM sales').fetchone()[0],1)
    def test_financial_history_append_only(self):
        self.sale()
        with self.assertRaises(sqlite3.IntegrityError):
            with self.db.transaction() as c: c.execute('DELETE FROM sales_financial_history')
    def test_negative_financial_evidence_rejected(self):
        with self.assertRaises(ValueError): self.sale(fees=-1)
    def test_profit_cross_check(self):
        self.sale()
        with self.db.connect() as c:
            r=c.execute("SELECT * FROM sales WHERE sale_id='S1'").fetchone()
            self.assertEqual(r['profit_minor'],r['revenue_minor']-r['marketplace_fees_minor']-r['shipping_minor']-r['packaging_minor']-r['cogs_minor'])
if __name__=='__main__': unittest.main()
