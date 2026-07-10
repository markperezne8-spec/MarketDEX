import sqlite3

import pytest

from core.database_manager import DatabaseManager
from repositories.settlement_repository import SettlementEvidenceConflict, SettlementRepository


def repository_with_parent(tmp_path):
    path = tmp_path / "marketdex.sqlite3"
    database = DatabaseManager(path)
    database.initialize()
    repository = SettlementRepository()
    with database.transaction() as c:
        repository.append_evidence(
            c, settlement_evidence_id="EVIDENCE-001", marketplace="EBAY",
            marketplace_settlement_reference="PAYOUT-001", settlement_date="2026-07-10",
            settlement_currency="USD", evidence_source_type="MARKETPLACE_REPORT",
            evidence_source_reference="REPORT-001", settlement_net_minor=12345,
            evidence_status="PENDING EVIDENCE", verification_result="PENDING",
            created_event_id="EVIDENCE-EVENT", created_at="2026-07-10",
        )
    return path, database, repository


@pytest.mark.parametrize(
    "status,sale_id,group_id",
    [
        ("", None, None),
        ("UNMATCHED", None, None),
        ("SINGLE_SALE_LINKED", "SALE-001", None),
        ("MULTI_SALE_PENDING_ALLOCATION", None, "GROUP-001"),
        ("ALLOCATED", None, "GROUP-001"),
    ],
)
def test_build483_canonical_linkage_vocabulary_and_unknown_preservation(tmp_path, status, sale_id, group_id):
    _, database, repository = repository_with_parent(tmp_path)
    with database.transaction() as c:
        row = repository.append_evidence_linkage(
            c, settlement_evidence_id="EVIDENCE-001", linkage_status=status,
            linked_sale_id=sale_id, allocation_group_id=group_id,
            created_event_id="LINK-EVENT", created_at="2026-07-10",
        )
    assert row["linkage_status"] == status
    assert row["linked_sale_id"] == sale_id
    assert row["allocation_group_id"] == group_id


@pytest.mark.parametrize(
    "status,sale_id,group_id",
    [
        ("NOT_CANONICAL", None, None),
        ("UNMATCHED", "SALE-001", None),
        ("SINGLE_SALE_LINKED", None, None),
        ("SINGLE_SALE_LINKED", "SALE-001", "GROUP-001"),
        ("MULTI_SALE_PENDING_ALLOCATION", "SALE-001", "GROUP-001"),
        ("ALLOCATED", None, None),
    ],
)
def test_build483_contradictory_linkage_identity_fails_closed(tmp_path, status, sale_id, group_id):
    _, database, repository = repository_with_parent(tmp_path)
    with pytest.raises(SettlementEvidenceConflict):
        with database.transaction() as c:
            repository.append_evidence_linkage(
                c, settlement_evidence_id="EVIDENCE-001", linkage_status=status,
                linked_sale_id=sale_id, allocation_group_id=group_id,
                created_event_id="LINK-EVENT", created_at="2026-07-10",
            )


def test_linkage_requires_parent_and_contradictory_replay_fails_closed(tmp_path):
    _, database, repository = repository_with_parent(tmp_path)
    with pytest.raises(SettlementEvidenceConflict, match="parent required"):
        with database.transaction() as c:
            repository.append_evidence_linkage(
                c, settlement_evidence_id="MISSING", linkage_status="UNMATCHED",
                created_event_id="MISSING-EVENT", created_at="2026-07-10",
            )
    with database.transaction() as c:
        first = repository.append_evidence_linkage(
            c, settlement_evidence_id="EVIDENCE-001", linkage_status="SINGLE_SALE_LINKED",
            linked_sale_id="SALE-001", created_event_id="LINK-EVENT", created_at="2026-07-10",
        )
        replay = repository.append_evidence_linkage(
            c, settlement_evidence_id="EVIDENCE-001", linkage_status="SINGLE_SALE_LINKED",
            linked_sale_id="SALE-001", created_event_id="LINK-EVENT", created_at="2026-07-10",
        )
    assert dict(first) == dict(replay)
    with pytest.raises(SettlementEvidenceConflict, match="Contradictory"):
        with database.transaction() as c:
            repository.append_evidence_linkage(
                c, settlement_evidence_id="EVIDENCE-001", linkage_status="UNMATCHED",
                created_event_id="LINK-EVENT-2", created_at="2026-07-11",
            )


def test_linkage_is_append_only_and_reconstructs_after_restart(tmp_path):
    path, database, repository = repository_with_parent(tmp_path)
    with database.transaction() as c:
        repository.append_evidence_linkage(
            c, settlement_evidence_id="EVIDENCE-001", linkage_status="ALLOCATED",
            allocation_group_id="GROUP-001", created_event_id="LINK-EVENT", created_at="2026-07-10",
        )
    with pytest.raises(sqlite3.IntegrityError):
        with database.transaction() as c:
            c.execute("UPDATE settlement_evidence_linkage SET linkage_status='UNMATCHED'")
    with pytest.raises(sqlite3.IntegrityError):
        with database.transaction() as c:
            c.execute("DELETE FROM settlement_evidence_linkage")
    restarted = DatabaseManager(path)
    restarted.initialize()
    with restarted.read_connection() as c:
        row = repository.evidence_linkage_by_id(c, "EVIDENCE-001")
    assert row["linkage_status"] == "ALLOCATED"
    assert row["allocation_group_id"] == "GROUP-001"
