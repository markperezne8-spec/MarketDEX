from datetime import date

import pytest

from reports.definitions import build_report_catalog
from reports.inventory_age_query import (
    INPUT_NOT_FOUND,
    InventoryAgeReportQueryResult,
)
from reports.inventory_age_query_request import InventoryAgeReportQueryRequest
from reports.purchase_source_performance_contract import PurchaseSourcePerformanceRequest
from reports.purchase_source_performance_query import PurchaseSourcePerformanceQueryResponse
from reports.report_query_request import ReportQueryRequest
from reports.report_query_service import ReportQueryService


class _InventoryAgeQuery:
    def __init__(self) -> None:
        self.requests = []

    def get_inventory_age_for_request(self, request):
        self.requests.append(request)
        return InventoryAgeReportQueryResult(INPUT_NOT_FOUND, reason='no approved evidence')


class _PurchaseSourceQuery:
    def __init__(self) -> None:
        self.requests = []

    def get_evidence_for_request(self, request):
        self.requests.append(request)
        return PurchaseSourcePerformanceQueryResponse(
            request=request,
            evidence=(),
            source_domains=('inventory', 'sale_completion'),
            source_coverage=('complete',),
            provenance=('test:cap-012-query-routing',),
        )


def _purchase_source_request() -> PurchaseSourcePerformanceRequest:
    return PurchaseSourcePerformanceRequest(
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
        as_of=date(2026, 2, 1),
        source_coverage_required=('inventory', 'sale_completion'),
    )


def test_build701aj_routes_catalog_approved_report_once() -> None:
    query = _InventoryAgeQuery()
    service = ReportQueryService(build_report_catalog(), query)
    request = InventoryAgeReportQueryRequest(' position-701aj ', date(2026, 7, 13))

    result = service.query_inventory_age_report(' INVENTORY-AGE-PATTERNS ', request)

    assert result.outcome == INPUT_NOT_FOUND
    assert query.requests == [request]


def test_cap012_routes_purchase_source_request_through_approved_boundary() -> None:
    inventory_query = _InventoryAgeQuery()
    purchase_source_query = _PurchaseSourceQuery()
    service = ReportQueryService(
        build_report_catalog(),
        inventory_query,
        purchase_source_query,
    )
    request = _purchase_source_request()

    result = service.query(
        ReportQueryRequest(
            ' PURCHASE-SOURCE-PERFORMANCE ',
            purchase_source_request=request,
        )
    )

    assert result.request == request
    assert purchase_source_query.requests == [request]
    assert inventory_query.requests == []


def test_cap012_fails_closed_when_purchase_source_boundary_is_unavailable() -> None:
    service = ReportQueryService(build_report_catalog(), _InventoryAgeQuery())
    request = _purchase_source_request()

    with pytest.raises(KeyError, match='unsupported executable report'):
        service.query(
            ReportQueryRequest(
                'purchase-source-performance',
                purchase_source_request=request,
            )
        )


def test_build701aj_rejects_unknown_report_before_query() -> None:
    query = _InventoryAgeQuery()
    service = ReportQueryService(build_report_catalog(), query)
    request = InventoryAgeReportQueryRequest('position-701aj', date(2026, 7, 13))

    with pytest.raises(KeyError, match='unknown report'):
        service.query_inventory_age_report('missing-report', request)

    assert query.requests == []


def test_build701al_rejects_non_contract_request_before_query() -> None:
    query = _InventoryAgeQuery()
    service = ReportQueryService(build_report_catalog(), query)

    with pytest.raises(TypeError, match='InventoryAgeReportQueryRequest'):
        service.query_inventory_age_report(
            'inventory-age-patterns',
            object(),
        )

    assert query.requests == []
