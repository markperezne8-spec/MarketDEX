from datetime import date
from decimal import Decimal

import pytest

from reports.inventory_turnover_calculator import (
    EVIDENCE_CONFLICTING,
    EVIDENCE_UNAVAILABLE,
    DeterministicInventoryTurnoverProvider,
    InventoryTurnoverEvidence,
)
from reports.inventory_turnover_contract import (
    OUTCOME_CONFLICT,
    OUTCOME_NO_ELIGIBLE_INVENTORY,
    OUTCOME_UNAVAILABLE,
    OUTCOME_VALID,
    OUTCOME_ZERO_TURNOVER,
    InventoryTurnoverReportRequest,
    InventoryTurnoverReportResult,
)
from reports.inventory_turnover_query import (
    InventoryTurnoverReportProvider,
    InventoryTurnoverReportQueryService,
)


def _request(*, group_by: str | None = None) -> InventoryTurnoverReportRequest:
    return InventoryTurnoverReportRequest(
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
        as_of=date(2026, 2, 2),
        source_coverage_required=('inventory', 'listing', 'audit'),
        group_by=group_by,
    )


def _unavailable_result(
    request: InventoryTurnoverReportRequest,
    reason: str = 'fixture unavailable evidence',
) -> InventoryTurnoverReportResult:
    return InventoryTurnoverReportResult(
        request=request,
        outcome=OUTCOME_UNAVAILABLE,
        reason=reason,
        source_domains=('audit', 'inventory', 'listing'),
        source_coverage=('unavailable',),
        evidence_state='unavailable',
        provenance=('test-provider:unavailable',),
    )


def _evidence(
    opening: int | None,
    closing: int | None,
    completed: int | None,
    *,
    state: str = 'available',
    reason: str = 'approved fixture evidence',
) -> InventoryTurnoverEvidence:
    return InventoryTurnoverEvidence(
        opening_eligible_inventory_units=opening,
        closing_eligible_inventory_units=closing,
        completed_sale_units=completed,
        source_domains=('audit', 'inventory', 'listing'),
        source_coverage=('closed_period',),
        provenance=('fixture:opening', 'fixture:closing', 'fixture:completed-sales'),
        evidence_state=state,
        reason=reason,
    )


class StaticInventoryTurnoverProvider:
    def __init__(self, result: InventoryTurnoverReportResult) -> None:
        self.result = result
        self.seen_request: InventoryTurnoverReportRequest | None = None

    def get_inventory_turnover_result(
        self,
        request: InventoryTurnoverReportRequest,
    ) -> InventoryTurnoverReportResult:
        self.seen_request = request
        return self.result


class FailingInventoryTurnoverProvider:
    def get_inventory_turnover_result(
        self,
        request: InventoryTurnoverReportRequest,
    ) -> InventoryTurnoverReportResult:
        raise RuntimeError('source dependency unavailable')


class UnsupportedInventoryTurnoverProvider:
    def get_inventory_turnover_result(
        self,
        request: InventoryTurnoverReportRequest,
    ) -> object:
        return object()


def test_inventory_turnover_provider_is_read_only_protocol() -> None:
    request = _request()
    provider = StaticInventoryTurnoverProvider(_unavailable_result(request))

    assert isinstance(provider, InventoryTurnoverReportProvider)
    assert not hasattr(provider, 'save')
    assert not hasattr(provider, 'execute')
    assert not hasattr(provider, 'export')


def test_inventory_turnover_query_service_delegates_immutable_request() -> None:
    request = _request()
    expected = _unavailable_result(request)
    provider = StaticInventoryTurnoverProvider(expected)
    service = InventoryTurnoverReportQueryService(provider)

    result = service.get_inventory_turnover_for_request(request)

    assert result is expected
    assert provider.seen_request is request
    assert result.request_id == request.request_id
    assert result.report_id == 'inventory-turnover'
    assert result.formula_id == 'inventory-turnover-units-v1'


def test_inventory_turnover_query_service_accepts_only_contract_request() -> None:
    service = InventoryTurnoverReportQueryService(FailingInventoryTurnoverProvider())

    with pytest.raises(TypeError, match='InventoryTurnoverReportRequest'):
        service.get_inventory_turnover_for_request(object())  # type: ignore[arg-type]


def test_inventory_turnover_query_service_fails_closed_when_provider_raises() -> None:
    request = _request()
    service = InventoryTurnoverReportQueryService(FailingInventoryTurnoverProvider())

    result = service.get_inventory_turnover_for_request(request)

    assert result.outcome == OUTCOME_UNAVAILABLE
    assert result.reason == 'Inventory Turnover provider unavailable'
    assert result.source_domains == ('audit', 'inventory', 'listing')
    assert result.source_coverage == ('unavailable',)
    assert result.evidence_state == 'unavailable'
    assert result.provenance == ('inventory-turnover-query-boundary:provider-unavailable',)
    assert result.opening_eligible_inventory_units is None
    assert result.closing_eligible_inventory_units is None
    assert result.average_eligible_inventory_units is None
    assert result.completed_sale_units is None
    assert result.turnover_ratio is None
    assert result.turnover_percentage is None


def test_inventory_turnover_query_service_fails_closed_for_bad_provider_result() -> None:
    request = _request()
    service = InventoryTurnoverReportQueryService(UnsupportedInventoryTurnoverProvider())  # type: ignore[arg-type]

    result = service.get_inventory_turnover_for_request(request)

    assert result.outcome == OUTCOME_UNAVAILABLE
    assert result.reason == 'Inventory Turnover provider returned unsupported result'
    assert result.turnover_ratio is None
    assert result.turnover_percentage is None


def test_deterministic_provider_calculates_valid_turnover() -> None:
    result = DeterministicInventoryTurnoverProvider(
        _evidence(10, 6, 4)
    ).get_inventory_turnover_result(_request())

    assert result.outcome == OUTCOME_VALID
    assert result.average_eligible_inventory_units == Decimal('8')
    assert result.turnover_ratio == Decimal('0.5')
    assert result.turnover_percentage == Decimal('50.0')


def test_deterministic_provider_preserves_zero_turnover() -> None:
    result = DeterministicInventoryTurnoverProvider(
        _evidence(8, 8, 0)
    ).get_inventory_turnover_result(_request())

    assert result.outcome == OUTCOME_ZERO_TURNOVER
    assert result.turnover_ratio == Decimal('0')
    assert result.turnover_percentage == Decimal('0')


def test_deterministic_provider_returns_no_inventory_for_all_zero_quantities() -> None:
    result = DeterministicInventoryTurnoverProvider(
        _evidence(0, 0, 0)
    ).get_inventory_turnover_result(_request())

    assert result.outcome == OUTCOME_NO_ELIGIBLE_INVENTORY
    assert result.opening_eligible_inventory_units == 0
    assert result.closing_eligible_inventory_units == 0
    assert result.completed_sale_units == 0
    assert result.turnover_ratio is None


def test_deterministic_provider_fails_closed_for_missing_quantities() -> None:
    result = DeterministicInventoryTurnoverProvider(
        _evidence(None, 5, 2)
    ).get_inventory_turnover_result(_request())

    assert result.outcome == OUTCOME_UNAVAILABLE
    assert result.turnover_ratio is None
    assert result.turnover_percentage is None


def test_deterministic_provider_preserves_conflicting_and_unavailable_evidence() -> None:
    conflict = DeterministicInventoryTurnoverProvider(
        _evidence(10, 6, 4, state=EVIDENCE_CONFLICTING, reason='quantity conflict')
    ).get_inventory_turnover_result(_request())
    unavailable = DeterministicInventoryTurnoverProvider(
        _evidence(None, None, None, state=EVIDENCE_UNAVAILABLE, reason='coverage missing')
    ).get_inventory_turnover_result(_request())

    assert conflict.outcome == OUTCOME_CONFLICT
    assert conflict.turnover_ratio is None
    assert unavailable.outcome == OUTCOME_UNAVAILABLE
    assert unavailable.completed_sale_units is None


def test_deterministic_provider_rejects_sales_with_zero_average_inventory() -> None:
    result = DeterministicInventoryTurnoverProvider(
        _evidence(0, 0, 1)
    ).get_inventory_turnover_result(_request())

    assert result.outcome == OUTCOME_CONFLICT
    assert result.turnover_ratio is None


def test_deterministic_provider_fails_closed_for_grouped_request() -> None:
    result = DeterministicInventoryTurnoverProvider(
        _evidence(10, 6, 4)
    ).get_inventory_turnover_result(_request(group_by='product_id'))

    assert result.outcome == OUTCOME_UNAVAILABLE
    assert result.reason == 'grouped Inventory Turnover results are not authorized'
    assert result.turnover_ratio is None
