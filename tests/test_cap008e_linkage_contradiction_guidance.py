import pytest

from services.settlement_linkage_guidance_service import SettlementLinkageGuidanceService


@pytest.fixture
def service():
    return SettlementLinkageGuidanceService()


def test_unknown_preserves_not_asserted_linkage(service):
    guidance = service.derive(None, None, None)

    assert guidance.result == "UNKNOWN"
    assert guidance.evidence_to_review == (
        "linkage_status",
        "linked_sale_id",
        "allocation_group_id",
    )
    assert guidance.authority == "ADVISORY ONLY — NO SETTLEMENT AUTHORITY"


@pytest.mark.parametrize(
    ("status", "sale_id", "group_id"),
    [
        ("UNMATCHED", None, None),
        ("SINGLE_SALE_LINKED", "SALE-001", None),
        ("MULTI_SALE_PENDING_ALLOCATION", None, None),
        ("MULTI_SALE_PENDING_ALLOCATION", None, "GROUP-001"),
        ("ALLOCATED", None, "GROUP-001"),
    ],
)
def test_canonical_linkage_identity_combinations_are_clear(service, status, sale_id, group_id):
    guidance = service.derive(status, sale_id, group_id)

    assert guidance.result == "CLEAR"
    assert guidance.evidence_to_review == ()
    assert guidance.authority == "ADVISORY ONLY — NO SETTLEMENT AUTHORITY"


@pytest.mark.parametrize(
    ("status", "sale_id", "group_id"),
    [
        ("", "SALE-001", None),
        ("", None, "GROUP-001"),
        ("UNMATCHED", "SALE-001", None),
        ("UNMATCHED", None, "GROUP-001"),
        ("SINGLE_SALE_LINKED", None, None),
        ("SINGLE_SALE_LINKED", "SALE-001", "GROUP-001"),
        ("MULTI_SALE_PENDING_ALLOCATION", "SALE-001", None),
        ("ALLOCATED", None, None),
        ("ALLOCATED", "SALE-001", "GROUP-001"),
        ("NON_CANONICAL", None, None),
    ],
)
def test_each_contradictory_identity_combination_returns_advisory_guidance(
    service, status, sale_id, group_id
):
    guidance = service.derive(status, sale_id, group_id)

    assert guidance.result == "CONTRADICTION"
    assert guidance.guidance
    assert guidance.evidence_to_review
    assert guidance.authority == "ADVISORY ONLY — NO SETTLEMENT AUTHORITY"


def test_guidance_derivation_is_read_only(service):
    linkage = {
        "settlement_evidence_id": "SET-EVIDENCE-001",
        "linkage_status": "SINGLE_SALE_LINKED",
        "linked_sale_id": "SALE-001",
        "allocation_group_id": None,
        "created_event_id": "EVENT-001",
        "created_at": "2026-07-12T00:00:00+00:00",
    }
    before = dict(linkage)

    first = service.derive_from_row(linkage)
    second = service.derive_from_row(linkage)

    assert first == second
    assert first.result == "CLEAR"
    assert linkage == before
