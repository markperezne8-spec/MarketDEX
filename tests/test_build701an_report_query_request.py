from datetime import date

import pytest

from reports.definitions import build_report_catalog
from reports.inventory_age_query import (
    INPUT_NOT_FOUND,
    InventoryAgeReportQueryResult,
)
from reports.inventory_age_query_request import InventoryAgeReportQueryRequest
from reports.report_query_request import ReportQueryRequest
from reports.report_query_service import ReportQueryService


class _InventoryAgeQuery:
    def __init__(self) -> None:
        self.requests = []

    def get_inventory_age_for_request(self, request):
        self.requests.append(request)
        return InventoryAgeReportQueryResult(INPUT_NOT_FOUND, reason='no approved evidence')


def test_build701an_envelope_normalizes_report_id_and_preserves_request() -> None:
    inventory_request = InventoryAgeReportQueryRequest(
        ' position-701an ',
        date(2026, 7, 13),
    )

    request = ReportQueryRequest(' INVENTORY-AGE-PATTERNS ', inventory_request)

    assert request.report_id == 'inventory-age-patterns'
    assert request.inventory_age_request is inventory_request


def test_build701an_envelope_routes_once() -> None:
    query = _InventoryAgeQuery()
    service = ReportQueryService(build_report_catalog(), query)
    inventory_request = InventoryAgeReportQueryRequest(
        'position-701an',
        date(2026, 7, 13),
    )

    result = service.query(
        ReportQueryRequest('inventory-age-patterns', inventory_request)
    )

    assert result.outcome == INPUT_NOT_FOUND
    assert query.requests == [inventory_request]


def test_build701an_rejects_invalid_envelope_request() -> None:
    with pytest.raises(TypeError, match='InventoryAgeReportQueryRequest'):
        ReportQueryRequest('inventory-age-patterns', object())
