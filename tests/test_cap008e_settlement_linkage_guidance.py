from services.settlement_linkage_guidance_service import SettlementLinkageGuidanceService


def test_unknown_blank_linkage_is_preserved_without_asserting_authority():
    result = SettlementLinkageGuidanceService().derive()

    assert result["contradiction_result"] == "UNKNOWN"
    assert result["review_fields"] == ("linkage_status",)
    assert result["guidance_authority"] == "ADVISORY ONLY — NO SETTLEMENT AUTHORITY"


def test_canonical_clear_linkage_combinations_are_deterministic():
    service = SettlementLinkageGuidanceService()
    clear_cases = (
        dict(linkage_status="UNMATCHED"),
        dict(linkage_status="SINGLE_SALE_LINKED", linked_sale_id="SALE-001"),
        dict(linkage_status="MULTI_SALE_PENDING_ALLOCATION", allocation_group_id="GROUP-001"),
        dict(linkage_status="ALLOCATED", allocation_group_id="GROUP-001"),
    )

    for case in clear_cases:
        result = service.derive(**case)
        assert result["contradiction_result"] == "CLEAR"
        assert result["review_fields"] == ()
        assert result["guidance_authority"] == "ADVISORY ONLY — NO SETTLEMENT AUTHORITY"


def test_each_canonical_contradiction_returns_targeted_read_only_guidance():
    service = SettlementLinkageGuidanceService()
    contradiction_cases = (
        dict(linkage_status="UNMATCHED", linked_sale_id="SALE-001"),
        dict(linkage_status="SINGLE_SALE_LINKED"),
        dict(linkage_status="SINGLE_SALE_LINKED", linked_sale_id="SALE-001", allocation_group_id="GROUP-001"),
        dict(linkage_status="MULTI_SALE_PENDING_ALLOCATION", linked_sale_id="SALE-001"),
        dict(linkage_status="ALLOCATED"),
        dict(linkage_status="ALLOCATED", linked_sale_id="SALE-001", allocation_group_id="GROUP-001"),
        dict(linkage_status="NOT_A_STATUS"),
    )

    for case in contradiction_cases:
        result = service.derive(**case)
        assert result["contradiction_result"] == "CONTRADICTION"
        assert result["review_fields"]
        assert result["resolution_guidance"]
        assert result["guidance_authority"] == "ADVISORY ONLY — NO SETTLEMENT AUTHORITY"


def test_guidance_service_has_no_database_or_repository_write_dependency():
    service = SettlementLinkageGuidanceService()

    assert not hasattr(service, "database")
    assert not hasattr(service, "repository")
    assert service.derive(linkage_status="ALLOCATED", allocation_group_id="GROUP-001")["contradiction_result"] == "CLEAR"
