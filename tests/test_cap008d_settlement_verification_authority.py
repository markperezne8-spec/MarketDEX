from core.database_manager import DatabaseManager
from repositories.settlement_repository import SettlementRepository


def authority(tmp_path, *, linkage_status="SINGLE_SALE_LINKED", sale_id="SALE-001",
              group_id=None, expected=1000, net=1000, tolerance=0,
              source_reference="REPORT-001"):
    db = DatabaseManager(tmp_path / "marketdex.sqlite3")
    db.initialize()
    repository = SettlementRepository()
    with db.transaction() as c:
        repository.append_evidence(
            c, settlement_evidence_id="EVIDENCE-001", marketplace="EBAY",
            marketplace_settlement_reference="PAYOUT-001", settlement_date="2026-07-10",
            settlement_currency="USD", evidence_source_type="MARKETPLACE_REPORT",
            evidence_source_reference=source_reference, settlement_net_minor=net,
            evidence_status="PENDING EVIDENCE", verification_result="PENDING",
            created_event_id="EVIDENCE-EVENT", created_at="2026-07-10",
        )
        repository.append_evidence_linkage(
            c, settlement_evidence_id="EVIDENCE-001", linkage_status=linkage_status,
            linked_sale_id=sale_id, allocation_group_id=group_id,
            created_event_id="LINK-EVENT", created_at="2026-07-10",
        )
    with db.read_connection() as c:
        return repository.verification_authority(
            c, "EVIDENCE-001", expected_settlement_minor=expected,
            tolerance_minor=tolerance,
        )


def test_builds487_497_verified_requires_traceable_resolved_cross_checked_evidence(tmp_path):
    result = authority(tmp_path)
    assert result == {
        "settlement_evidence_status": "VERIFIED",
        "settlement_verification_result": "SETTLEMENT VERIFIED",
        "cross_check_difference_minor": 0,
        "verification_authority": "SETTLEMENT AUTHORITY ONLY — NO TAX OR SETTLEMENT COMPLETION AUTHORITY",
    }


def test_builds487_497_unmatched_and_pending_allocation_fail_closed(tmp_path):
    unmatched = authority(tmp_path / "unmatched", linkage_status="UNMATCHED", sale_id=None)
    pending = authority(
        tmp_path / "pending", linkage_status="MULTI_SALE_PENDING_ALLOCATION",
        sale_id=None, group_id=None,
    )
    for result in (unmatched, pending):
        assert result["settlement_evidence_status"] == "EVIDENCE_COMPLETE"
        assert result["settlement_verification_result"] == "NOT READY"
        assert result["cross_check_difference_minor"] is None
        assert result["verification_authority"] == "NO SETTLEMENT AUTHORITY — FAIL CLOSED"


def test_builds487_497_missing_comparison_basis_remains_pending(tmp_path):
    result = authority(tmp_path, expected=None)
    assert result["settlement_evidence_status"] == "CROSS_CHECK_PENDING"
    assert result["settlement_verification_result"] == "PENDING"
    assert result["cross_check_difference_minor"] is None


def test_builds487_497_difference_derives_only_with_comparison_basis_and_exception_preserves_truth(tmp_path):
    result = authority(tmp_path, expected=1200, net=1000)
    assert result["settlement_evidence_status"] == "EXCEPTION"
    assert result["settlement_verification_result"] == "SETTLEMENT EXCEPTION"
    assert result["cross_check_difference_minor"] == 200
    assert result["verification_authority"] == "NO SETTLEMENT AUTHORITY — FAIL CLOSED"


def test_builds487_497_controlled_tolerance_can_verify_without_completion_or_tax_authority(tmp_path):
    result = authority(tmp_path, expected=1002, net=1000, tolerance=2)
    assert result["settlement_verification_result"] == "SETTLEMENT VERIFIED"
    assert result["cross_check_difference_minor"] == 2
    assert "NO TAX OR SETTLEMENT COMPLETION AUTHORITY" in result["verification_authority"]


def test_builds487_497_allocated_linkage_is_resolved_without_sale_level_identity(tmp_path):
    result = authority(
        tmp_path, linkage_status="ALLOCATED", sale_id=None, group_id="ALG-000001",
    )
    assert result["settlement_verification_result"] == "SETTLEMENT VERIFIED"


def test_builds487_497_blank_linkage_is_unknown_and_fails_closed(tmp_path):
    result = authority(tmp_path, linkage_status="", sale_id=None)
    assert result["settlement_verification_result"] == "NOT READY"
    assert result["cross_check_difference_minor"] is None
    assert result["verification_authority"] == "NO SETTLEMENT AUTHORITY — FAIL CLOSED"
