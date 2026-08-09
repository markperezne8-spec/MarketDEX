from datetime import date
from pathlib import Path

from composition.application_composition import ApplicationComposition
from reports.definitions import PURCHASE_SOURCE_PERFORMANCE_REPORT
from reports.purchase_source_performance_contract import PurchaseSourcePerformanceRequest
from reports.purchase_source_performance_query import PurchaseSourcePerformanceQueryResponse
from reports.report_query_request import ReportQueryRequest


def test_catalog_and_composition_register_purchase_source_performance(tmp_path):
    composition = ApplicationComposition(Path(tmp_path) / 'marketdex.sqlite3')
    assert composition.get_report_definition('purchase-source-performance') == PURCHASE_SOURCE_PERFORMANCE_REPORT
    assert 'purchase-source-performance' in composition.report_catalog.report_ids


def test_query_routing_preserves_exact_request(tmp_path):
    composition = ApplicationComposition(Path(tmp_path) / 'marketdex.sqlite3')
    request = PurchaseSourcePerformanceRequest(date(2026, 7, 1), date(2026, 8, 1), date(2026, 8, 1), ('inventory',))
    response = composition.report_query.query(ReportQueryRequest('purchase-source-performance', purchase_source_request=request))
    assert isinstance(response, PurchaseSourcePerformanceQueryResponse)
    assert response.request == request
    assert response.source_coverage
