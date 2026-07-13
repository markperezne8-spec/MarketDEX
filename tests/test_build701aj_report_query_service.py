from datetime import date

import pytest

from reports.definitions import build_report_catalog
from reports.inventory_age_query import (
    INPUT_NOT_FOUND,
    InventoryAgeReportQueryResult,
)
from reports.inventory_age_query_request import InventoryAgeReportQueryRequest
from reports.report_query_service import ReportQueryService


class _InventoryAgeQuery:
    def __init__(self) -> None:
        self.requests = []

    def get_inventory_age_for_request(self, request):
        self.requests.append(request)
        return InventoryAgeReportQueryResult(INPUT_NOT_FOUND, reason='no approved evidence')


def test_build701aj_routes_catalog_approved_report_once() -> None:
    query = _InventoryAgeQuery()
    service = ReportQueryService(build_report_catalog(), query)
    request = InventoryAgeReportQueryRequest(' position-701aj ', date(2026, 7, 13))

    result = service.query_inventory_age_report(' INVENTORY-AGE-PATTERNS ', request)

    assert result.outcome == INPUT_NOT_FOUND
    assert query.requests == [request]


def test_build701aj_rejects_unknown_report_before_query() -> None:
    query = _InventoryAgeQuery()
    service = ReportQueryService(build_report_catalog(), query)
    request = InventoryAgeReportQueryRequest('position-701aj', date(2026, 7, 13))

    with pytest.raises(KeyError, match='unknown report'):
        service.query_inventory_age_report('missing-report', request)

    assert query.requests == []
