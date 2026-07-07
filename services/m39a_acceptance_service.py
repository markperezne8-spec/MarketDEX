from pathlib import Path
from core.database_manager import DatabaseManager
from services.m38_acceptance_service import M38AcceptanceService
from services.product_sale_execution_service import SALE_ID
from services.settlement_service import SettlementService, SettlementBlocked

SETTLEMENT_ID = "SETTLEMENT-M39A-001"
SETTLEMENT_REQUEST_ID = "M39A-SETTLEMENT-REQUEST-001"
SETTLEMENT_EVIDENCE_ID = "M39A-EBAY-PAYOUT-EVIDENCE-001"


class M39AAcceptanceService:
    def __init__(self, path):
        self.path = Path(path)
        self.settlement = SettlementService(self.path)

    def _ensure_sale(self):
        m38 = M38AcceptanceService(self.path)
        result = m38.execute()
        if result["passed"] != 12:
            raise RuntimeError("M38 accepted sale authority incomplete")

    def execute(self):
        self._ensure_sale()
        with self.settlement.database.read_connection() as c:
            financial = c.execute(
                "SELECT * FROM sales_financial_history WHERE sale_id=?", (SALE_ID,)
            ).fetchone()
            expected = (
                int(financial["revenue_minor"])
                - int(financial["marketplace_fees_minor"])
                - int(financial["shipping_minor"])
                - int(financial["packaging_minor"])
            )
        kwargs = dict(
            settlement_id=SETTLEMENT_ID,
            sale_id=SALE_ID,
            settlement_request_id=SETTLEMENT_REQUEST_ID,
            settlement_evidence_id=SETTLEMENT_EVIDENCE_ID,
            settlement_platform="eBay",
            observed_payout_minor=expected,
            evidence_complete=True,
            intent="SETTLE",
        )
        self.settlement.execute_settlement(**kwargs)
        self.settlement.execute_settlement(**kwargs)
        restarted = SettlementService(self.path)
        restarted.execute_settlement(**kwargs)
        self.settlement = restarted
        return self.verify()

    def verify(self):
        db = DatabaseManager(self.path)
        db.initialize()
        with db.read_connection() as c:
            sale = c.execute("SELECT * FROM sales WHERE sale_id=?", (SALE_ID,)).fetchone()
            fin = c.execute("SELECT * FROM sales_financial_history WHERE sale_id=?", (SALE_ID,)).fetchall()
            sold = c.execute("SELECT * FROM publication_lifecycle_events WHERE sale_id=? AND event_type='SOLD_CONVERSION'", (SALE_ID,)).fetchall()
            settlement = c.execute("SELECT * FROM settlement_executions WHERE settlement_id=?", (SETTLEMENT_ID,)).fetchone()
            history = c.execute("SELECT * FROM settlement_history WHERE settlement_id=?", (SETTLEMENT_ID,)).fetchall()
            replay = c.execute("SELECT * FROM replay_defense_history WHERE request_id=? AND attempted_event_type='SETTLEMENT'", (SETTLEMENT_REQUEST_ID,)).fetchall()
            sale_event = None if sale is None else c.execute("SELECT * FROM event_identity WHERE event_id=? AND event_type='SALE'", (sale["created_event_id"],)).fetchone()
            settlement_event = None if settlement is None else c.execute("SELECT * FROM event_identity WHERE event_id=? AND event_type='SETTLEMENT'", (settlement["settlement_event_id"],)).fetchone()
            audit = None if settlement is None else c.execute("SELECT * FROM audit_events WHERE event_id=? AND authority_type='SETTLEMENT' AND authority_id=?", (settlement["settlement_event_id"], SETTLEMENT_ID)).fetchone()
            inventory = None if sale is None else c.execute("SELECT quantity FROM inventory_authority WHERE asset_id=?", (sale["asset_id"],)).fetchone()
            sale_count = c.execute("SELECT COUNT(*) n FROM sales WHERE sale_id=?", (SALE_ID,)).fetchone()["n"]
            order_closure_count = c.execute("SELECT COUNT(*) n FROM order_closures").fetchone()["n"]
            inv_sale_moves = 0 if sale is None else c.execute("SELECT COUNT(*) n FROM inventory_history WHERE event_id=?", (sale["created_event_id"],)).fetchone()["n"]
            settlement_inv_moves = 0 if settlement is None else c.execute("SELECT COUNT(*) n FROM inventory_history WHERE event_id=?", (settlement["settlement_event_id"],)).fetchone()["n"]
            expected = None if not fin else (int(fin[0]["revenue_minor"]) - int(fin[0]["marketplace_fees_minor"]) - int(fin[0]["shipping_minor"]) - int(fin[0]["packaging_minor"]))

        sale_ok = sale is not None and sale_count == 1
        sale_event_ok = sale_event is not None and len(sold) == 1 and sold[0]["marketplace"] == "eBay"
        fin_ok = len(fin) == 1 and fin[0]["event_id"] == sale["created_event_id"] if sale else False
        expected_ok = expected is not None and expected >= 0
        evidence_ok = settlement is not None and settlement["settlement_evidence_id"] == SETTLEMENT_EVIDENCE_ID
        platform_ok = settlement is not None and settlement["settlement_platform"] == sold[0]["marketplace"] if sold else False
        request_ok = settlement_event is not None and settlement["settlement_request_id"] == SETTLEMENT_REQUEST_ID
        service_ok = settlement is not None and settlement["settlement_result"] == "SETTLED"
        exactly_once = len(history) == 1 and sale_count == 1
        zero_mutation = inventory is not None and int(inventory["quantity"]) == 1 and inv_sale_moves == 1 and settlement_inv_moves == 0 and len(fin) == 1
        history_ok = len(history) == 1 and audit is not None and len(sold) == 1
        replay_restart_ok = len(replay) == 1 and len(history) == 1

        checks = [
            ("Authoritative sale identity", sale_ok, SALE_ID),
            ("Sale event + platform identity", sale_event_ok, "SALE / eBay"),
            ("M24 financial truth relationship", fin_ok, "VERIFIED"),
            ("Expected net proceeds authority", expected_ok, expected),
            ("Settlement evidence validation", evidence_ok, SETTLEMENT_EVIDENCE_ID),
            ("Settlement platform match", platform_ok, "eBay = eBay"),
            ("Explicit settlement request + event identity", request_ok, SETTLEMENT_REQUEST_ID),
            ("Standalone SettlementService execution", service_ok, "SETTLED"),
            ("Exactly-once SETTLED execution + zero second sale", exactly_once, "1 settlement / 1 sale"),
            ("Zero inventory mutation + zero duplicate M24 financial event", zero_mutation, "quantity 1 / financial 1"),
            ("Append-only settlement history + preserved SOLD lineage", history_ok, "history 1 / SOLD 1"),
            ("Persistent replay + restart protection", replay_restart_ok, "PASS / PASS"),
        ]
        passed = sum(1 for _, ok, _ in checks if ok)
        return {
            "checks": checks, "passed": passed,
            "sale_identity": "VERIFIED" if sale_ok else "BLOCKED",
            "sale_event": "VERIFIED" if sale_event_ok else "BLOCKED",
            "platform": "VERIFIED" if platform_ok else "BLOCKED",
            "financial": "VERIFIED" if fin_ok else "BLOCKED",
            "expected": "VERIFIED" if expected_ok else "BLOCKED",
            "evidence": "VERIFIED" if evidence_ok else "BLOCKED",
            "settlement": "SETTLED" if service_ok else "BLOCKED",
            "second_sale": "NO" if sale_count == 1 else "YES",
            "inventory_mutation": "ZERO" if settlement_inv_moves == 0 else "DETECTED",
            "second_financial": "NO" if len(fin) == 1 else "YES",
            "order_closure": "NO" if order_closure_count == 0 else "YES",
            "replay": "PASS" if replay_restart_ok else "FAIL",
            "restart": "PASS" if replay_restart_ok else "FAIL",
            "result": "STANDALONE SETTLEMENT VERIFIED" if passed == 12 else "BLOCKED",
        }
