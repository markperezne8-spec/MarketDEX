from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from repositories.settlement_repository import SettlementRepository
from services.base_service import AuthoritativeService


class SettlementBlocked(RuntimeError):
    pass


class SettlementService(AuthoritativeService):
    """M39A authority. Reads M24/M30 truth and owns only standalone SETTLED execution."""

    service_name = "settlement_service"

    def __init__(self, path):
        self.path = Path(path)
        self.database = DatabaseManager(self.path)
        self.database.initialize()
        self.events = EventRepository()
        self.repository = SettlementRepository()
        super().__init__(self.database, self.events)

    def _load_authority(self, c, *, sale_id, settlement_platform):
        sale = c.execute(
            "SELECT * FROM sales WHERE sale_id=? AND state='COMPLETED'", (sale_id,)
        ).fetchone()
        if sale is None:
            raise SettlementBlocked("Authoritative completed sale required")
        sale_event = c.execute(
            "SELECT * FROM event_identity WHERE event_id=? AND event_type='SALE'",
            (sale["created_event_id"],),
        ).fetchone()
        if sale_event is None:
            raise SettlementBlocked("Sale event identity relationship required")
        financial = c.execute(
            "SELECT * FROM sales_financial_history WHERE sale_id=? AND event_id=?",
            (sale_id, sale["created_event_id"]),
        ).fetchone()
        if financial is None:
            raise SettlementBlocked("Authoritative M24 financial history relationship required")
        financial_count = int(c.execute(
            "SELECT COUNT(*) n FROM sales_financial_history WHERE sale_id=?", (sale_id,)
        ).fetchone()["n"])
        if financial_count != 1:
            raise SettlementBlocked("Ambiguous M24 financial history relationship")
        sold = c.execute(
            """SELECT * FROM publication_lifecycle_events
               WHERE sale_id=? AND sale_event_id=? AND event_type='SOLD_CONVERSION'
               ORDER BY lifecycle_id""",
            (sale_id, sale["created_event_id"]),
        ).fetchall()
        if len(sold) != 1:
            raise SettlementBlocked("Authoritative sale platform relationship required")
        sale_platform = sold[0]["marketplace"]
        if not str(sale_platform).strip():
            raise SettlementBlocked("Authoritative sale platform required")
        if sale_platform != settlement_platform:
            raise SettlementBlocked("Settlement platform mismatch")
        expected = (
            int(financial["revenue_minor"])
            - int(financial["marketplace_fees_minor"])
            - int(financial["shipping_minor"])
            - int(financial["packaging_minor"])
        )
        if expected < 0:
            raise SettlementBlocked("Invalid expected net proceeds authority")
        return sale, sale_event, financial, sold[0], expected

    def _record_replay(self, request_id, event_id, payload_sha256, recorded_at):
        with self.database.transaction() as c:
            c.execute(
                """INSERT OR IGNORE INTO replay_defense_history(
                   request_id,original_event_id,attempted_event_type,payload_sha256,
                   defense_result,recorded_at) VALUES (?,?,?,?, 'BLOCKED',?)""",
                (request_id, event_id, "SETTLEMENT", payload_sha256, recorded_at),
            )

    def execute_settlement(self, *, settlement_id, sale_id, settlement_request_id,
                           settlement_evidence_id, settlement_platform,
                           observed_payout_minor, evidence_complete, intent):
        required = (
            settlement_id, sale_id, settlement_request_id,
            settlement_evidence_id, settlement_platform,
        )
        if not all(str(v).strip() for v in required):
            raise SettlementBlocked("Complete settlement identity evidence required")
        if str(intent).strip().upper() != "SETTLE":
            raise SettlementBlocked("Explicit settlement request required")
        if evidence_complete is not True:
            raise SettlementBlocked("Complete settlement evidence required")
        try:
            observed = int(observed_payout_minor)
        except (TypeError, ValueError):
            raise SettlementBlocked("Invalid observed payout amount")
        if observed < 0:
            raise SettlementBlocked("Invalid observed payout amount")

        payload = {
            "settlement_id": settlement_id,
            "sale_id": sale_id,
            "settlement_evidence_id": settlement_evidence_id,
            "settlement_platform": settlement_platform,
            "observed_payout_minor": observed,
        }
        event = self._new_event("SETTLEMENT", settlement_request_id, payload)

        with self.database.read_connection() as c:
            prior_event = c.execute(
                "SELECT * FROM event_identity WHERE request_id=?", (settlement_request_id,)
            ).fetchone()
            if prior_event is not None:
                accepted = self.repository.by_request_id(c, settlement_request_id)
                if (accepted is None or accepted["settlement_id"] != settlement_id
                        or accepted["sale_id"] != sale_id
                        or prior_event["payload_sha256"] != event.payload_sha256):
                    raise SettlementBlocked("Settlement request identity mismatch")
                event_id = prior_event["event_id"]
                payload_sha = prior_event["payload_sha256"]
                committed_at = prior_event["committed_at"]
            else:
                event_id = payload_sha = committed_at = None
                self._load_authority(c, sale_id=sale_id, settlement_platform=settlement_platform)
                if self.repository.by_sale_id(c, sale_id) is not None:
                    raise SettlementBlocked("Second settlement blocked")

        if event_id is not None:
            self._record_replay(settlement_request_id, event_id, payload_sha, committed_at)
            return self.get_settlement(settlement_id)

        # Immediate pre-execution authority revalidation occurs inside the write transaction.
        with self.database.transaction() as c:
            sale, sale_event, financial, sold, expected = self._load_authority(
                c, sale_id=sale_id, settlement_platform=settlement_platform
            )
            if observed != expected:
                raise SettlementBlocked("Observed payout does not satisfy expected net proceeds contract")
            if self.repository.by_sale_id(c, sale_id) is not None:
                raise SettlementBlocked("Second settlement blocked")
            inv_before = c.execute(
                "SELECT quantity FROM inventory_authority WHERE asset_id=?", (sale["asset_id"],)
            ).fetchone()["quantity"]
            sales_before = c.execute("SELECT COUNT(*) n FROM sales").fetchone()["n"]
            fin_before = c.execute("SELECT COUNT(*) n FROM sales_financial_history").fetchone()["n"]
            sold_before = c.execute(
                "SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'"
            ).fetchone()["n"]
            close_before = c.execute(
                "SELECT COUNT(*) n FROM event_identity WHERE event_type='ORDER_CLOSE'"
            ).fetchone()["n"]

            self._append_event_and_audit(c, event, "execute_settlement")
            self.repository.append(
                c, settlement_id=settlement_id, sale_id=sale_id,
                settlement_request_id=settlement_request_id,
                settlement_event_id=event.event_id,
                settlement_evidence_id=settlement_evidence_id,
                settlement_platform=settlement_platform,
                observed_payout_minor=observed,
                settlement_result="SETTLED", created_at=event.committed_at,
            )
            c.execute(
                """INSERT INTO audit_events(event_id,authority_type,authority_id,
                   verification_result,recorded_at) VALUES (?,?,?,?,?)""",
                (event.event_id, "SETTLEMENT", settlement_id, "VERIFIED", event.committed_at),
            )
            self._verify_event(c, event)

            if c.execute("SELECT COUNT(*) n FROM sales").fetchone()["n"] != sales_before:
                raise RuntimeError("Settlement created a second sale")
            if c.execute("SELECT COUNT(*) n FROM sales_financial_history").fetchone()["n"] != fin_before:
                raise RuntimeError("Settlement mutated M24 financial history")
            if c.execute(
                "SELECT quantity FROM inventory_authority WHERE asset_id=?", (sale["asset_id"],)
            ).fetchone()["quantity"] != inv_before:
                raise RuntimeError("Settlement mutated inventory")
            if c.execute(
                "SELECT COUNT(*) n FROM publication_lifecycle_events WHERE event_type='SOLD_CONVERSION'"
            ).fetchone()["n"] != sold_before:
                raise RuntimeError("Settlement created SOLD conversion")
            if c.execute(
                "SELECT COUNT(*) n FROM event_identity WHERE event_type='ORDER_CLOSE'"
            ).fetchone()["n"] != close_before:
                raise RuntimeError("Settlement created order closure")

        return self.get_settlement(settlement_id)

    def get_settlement(self, settlement_id):
        with self.database.read_connection() as c:
            row = self.repository.by_id(c, settlement_id)
            if row is None:
                raise SettlementBlocked("Unknown settlement")
            event = c.execute(
                "SELECT * FROM event_identity WHERE event_id=? AND event_type='SETTLEMENT'",
                (row["settlement_event_id"],),
            ).fetchone()
            history = self.repository.history_for(c, settlement_id)
            audit = c.execute(
                """SELECT * FROM audit_events WHERE event_id=? AND authority_type='SETTLEMENT'
                   AND authority_id=? AND verification_result='VERIFIED'""",
                (row["settlement_event_id"], settlement_id),
            ).fetchone()
            if event is None or len(history) != 1 or audit is None:
                raise SettlementBlocked("Settlement authority reconstruction failed")
            return dict(row)
