import sqlite3

import pytest

from core.database_manager import DatabaseManager
from repositories.settlement_repository import SettlementEvidenceConflict, SettlementRepository


def evidence_values(**overrides):
    values = {
        "settlement_evidence_id": "EVIDENCE-001",
        "marketplace": "EBAY",
        "marketplace_settlement_reference": "PAYOUT-001",
        "settlement_date": "2026-07-10T12:00:00Z",
        "settlement_currency": "USD",
        "evidence_source_type": "MARKETPLACE_REPORT",
        "evidence_source_reference": "REPORT-001",
        "settlement_net_minor": 12345,
        "evidence_status": "VERIFIED",
        "verification_result": "VERIFIED",
        "created_event_id": "EVENT-001",
        "created_at": "2026-07-10T12:00:00Z",
        "settlement_gross_minor": None,
        "settlement_fee_minor": None,
        "settlement_adjustment_minor": None,
    }
    values.update(overrides)
    return values


def test_parent_persists_without_sale_and_unknown_components_remain_null(tmp_path):
    path = tmp_path / "marketdex.sqlite3"
    database = DatabaseManager(path)
    database.initialize()
    repository = SettlementRepository()

    with database.transaction() as c:
        repository.append_evidence(c, **evidence_values())

    with database.read_connection() as c:
        row = repository.evidence_by_id(c, "EVIDENCE-001")
        assert row is not None
        assert row["settlement_gross_minor"] is None
        assert row["settlement_fee_minor"] is None
        assert row["settlement_adjustment_minor"] is None
        assert c.execute("SELECT COUNT(*) n FROM sales").fetchone()["n"] == 0
        assert c.execute("SELECT COUNT(*) n FROM settlement_executions").fetchone()["n"] == 0


def test_parent_reconstructs_after_restart_and_identical_replay_is_idempotent(tmp_path):
    path = tmp_path / "marketdex.sqlite3"
    database = DatabaseManager(path)
    database.initialize()
    repository = SettlementRepository()
    with database.transaction() as c:
        repository.append_evidence(c, **evidence_values())
        repository.append_evidence(c, **evidence_values())

    restarted = DatabaseManager(path)
    restarted.initialize()
    with restarted.read_connection() as c:
        row = repository.evidence_by_id(c, "EVIDENCE-001")
        assert row["settlement_net_minor"] == 12345
        assert c.execute("SELECT COUNT(*) n FROM settlement_evidence").fetchone()["n"] == 1


def test_contradictory_parent_evidence_fails_closed(tmp_path):
    path = tmp_path / "marketdex.sqlite3"
    database = DatabaseManager(path)
    database.initialize()
    repository = SettlementRepository()
    with database.transaction() as c:
        repository.append_evidence(c, **evidence_values())

    with pytest.raises(SettlementEvidenceConflict):
        with database.transaction() as c:
            repository.append_evidence(c, **evidence_values(settlement_net_minor=12346))

    with database.read_connection() as c:
        row = repository.evidence_by_id(c, "EVIDENCE-001")
        assert row["settlement_net_minor"] == 12345


def test_parent_is_append_only(tmp_path):
    path = tmp_path / "marketdex.sqlite3"
    database = DatabaseManager(path)
    database.initialize()
    repository = SettlementRepository()
    with database.transaction() as c:
        repository.append_evidence(c, **evidence_values())

    with pytest.raises(sqlite3.IntegrityError):
        with database.transaction() as c:
            c.execute("UPDATE settlement_evidence SET settlement_net_minor=1")
    with pytest.raises(sqlite3.IntegrityError):
        with database.transaction() as c:
            c.execute("DELETE FROM settlement_evidence")
