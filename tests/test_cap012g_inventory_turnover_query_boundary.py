from datetime import date

import pytest

from reports.inventory_turnover_contract import (
    OUTCOME_UNAVAILABLE,
    InventoryTurnoverReportRequest,
    InventoryTurnoverReportResult,
)
from reports.inventory_turnover_query import (
    InventoryTurnoverReportProvider,
    InventoryTurnoverReportQueryService,
)


def _request() -> InventoryTurnoverReportRequest:
    return InventoryTurnoverReportRequest(
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
        as_of=date(2026, 2, 2),
        source_coverage_required=('inventory', 'listing', 'audit'),
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
