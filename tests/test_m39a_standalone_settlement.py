import sqlite3
import pytest
from services.m38_acceptance_service import M38AcceptanceService
from services.product_sale_execution_service import SALE_ID
from services.settlement_service import SettlementService, SettlementBlocked
from services.m39a_acceptance_service import (
    M39AAcceptanceService, SETTLEMENT_ID, SETTLEMENT_REQUEST_ID, SETTLEMENT_EVIDENCE_ID,
)


def sale_fixture(path):
    result = M38AcceptanceService(path).execute()
    assert result["passed"] == 12
    svc = SettlementService(path)
    with svc.database.read_connection() as c:
        f = c.execute("SELECT * FROM sales_financial_history WHERE sale_id=?", (SALE_ID,)).fetchone()
        expected = int(f["revenue_minor"]) - int(f["marketplace_fees_minor"]) - int(f["shipping_minor"]) - int(f["packaging_minor"])
    return svc, expected


def kwargs(expected, **changes):
    values = dict(
        settlement_id=SETTLEMENT_ID, sale_id=SALE_ID,
        settlement_request_id=SETTLEMENT_REQUEST_ID,
        settlement_evidence_id=SETTLEMENT_EVIDENCE_ID,
        settlement_platform="eBay", observed_payout_minor=expected,
        evidence_complete=True, intent="SETTLE",
    )
    values.update(changes)
    return values


def test_m39a_exact_acceptance_12_of_12(tmp_path):
    result = M39AAcceptanceService(tmp_path / "m39a.sqlite3").execute()
    assert result["passed"] == 12
    assert result["result"] == "STANDALONE SETTLEMENT VERIFIED"
    assert result["inventory_mutation"] == "ZERO"
    assert result["second_sale"] == "NO"
    assert result["second_financial"] == "NO"
    assert result["order_closure"] == "NO"
    assert result["replay"] == result["restart"] == "PASS"


def test_unknown_sale_and_incomplete_evidence_fail_closed(tmp_path):
    svc = SettlementService(tmp_path / "blocked.sqlite3")
    with pytest.raises(SettlementBlocked):
        svc.execute_settlement(**kwargs(4200, sale_id="UNKNOWN"))
    svc, expected = sale_fixture(tmp_path / "sale.sqlite3")
    with pytest.raises(SettlementBlocked):
        svc.execute_settlement(**kwargs(expected, settlement_evidence_id=""))
    with pytest.raises(SettlementBlocked):
        svc.execute_settlement(**kwargs(expected, evidence_complete=False))
    with svc.database.read_connection() as c:
        assert c.execute("SELECT COUNT(*) n FROM settlement_executions").fetchone()["n"] == 0


def test_platform_and_payout_contract_fail_closed(tmp_path):
    svc, expected = sale_fixture(tmp_path / "contracts.sqlite3")
    with pytest.raises(SettlementBlocked):
        svc.execute_settlement(**kwargs(expected, settlement_platform="TCGplayer"))
    with pytest.raises(SettlementBlocked):
        svc.execute_settlement(**kwargs(expected, observed_payout_minor=expected - 1))
    with svc.database.read_connection() as c:
        assert c.execute("SELECT COUNT(*) n FROM settlement_executions").fetchone()["n"] == 0
        assert c.execute("SELECT COUNT(*) n FROM event_identity WHERE event_type='SETTLEMENT'").fetchone()["n"] == 0


def test_missing_and_orphan_financial_relationship_blocked(tmp_path):
    path = tmp_path / "financial.sqlite3"
    svc, expected = sale_fixture(path)
    with svc.database.transaction() as c:
        c.execute("DELETE FROM sales_financial_history WHERE sale_id=?", (SALE_ID,))
    with pytest.raises(SettlementBlocked):
        svc.execute_settlement(**kwargs(expected))
    with svc.database.read_connection() as c:
        assert c.execute("SELECT COUNT(*) n FROM settlement_executions").fetchone()["n"] == 0


def test_duplicate_request_and_restart_are_exactly_once(tmp_path):
    path = tmp_path / "replay.sqlite3"
    svc, expected = sale_fixture(path)
    first = svc.execute_settlement(**kwargs(expected))
    second = svc.execute_settlement(**kwargs(expected))
    third = SettlementService(path).execute_settlement(**kwargs(expected))
    assert first["settlement_event_id"] == second["settlement_event_id"] == third["settlement_event_id"]
    with svc.database.read_connection() as c:
        assert c.execute("SELECT COUNT(*) n FROM settlement_executions").fetchone()["n"] == 1
        assert c.execute("SELECT COUNT(*) n FROM settlement_history").fetchone()["n"] == 1
        assert c.execute("SELECT COUNT(*) n FROM replay_defense_history WHERE request_id=?", (SETTLEMENT_REQUEST_ID,)).fetchone()["n"] == 1
        assert c.execute("SELECT COUNT(*) n FROM event_identity WHERE event_type='ORDER_CLOSE'").fetchone()["n"] == 0


def test_settlement_history_is_append_only(tmp_path):
    path = tmp_path / "append.sqlite3"
    svc, expected = sale_fixture(path)
    svc.execute_settlement(**kwargs(expected))
    with pytest.raises(sqlite3.IntegrityError):
        with svc.database.transaction() as c:
            c.execute("UPDATE settlement_history SET settlement_result='SETTLED' WHERE settlement_id=?", (SETTLEMENT_ID,))
    with pytest.raises(sqlite3.IntegrityError):
        with svc.database.transaction() as c:
            c.execute("DELETE FROM settlement_executions WHERE settlement_id=?", (SETTLEMENT_ID,))
