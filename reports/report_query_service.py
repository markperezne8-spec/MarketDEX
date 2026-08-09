from __future__ import annotations

from collections.abc import Callable
from datetime import date

from reports.definitions import ReportCatalog
from reports.inventory_age_query import (
    InventoryAgeReportQueryResult,
    InventoryAgeReportQueryService,
)
from reports.inventory_age_query_request import InventoryAgeReportQueryRequest
from reports.report_query_request import ReportQueryRequest
from reports.purchase_source_performance_query import PurchaseSourcePerformanceQueryResponse, PurchaseSourcePerformanceQueryService


class ReportQueryService:
    """Routes catalog-approved report requests to read-only query services."""

    def __init__(
        self,
        catalog: ReportCatalog,
        inventory_age_query: InventoryAgeReportQueryService,
        purchase_source_performance_query: PurchaseSourcePerformanceQueryService | None = None,
    ) -> None:
        self._catalog = catalog
        self._inventory_age_query = inventory_age_query
        self._purchase_source_performance_query = purchase_source_performance_query

    def query(
        self,
        request: ReportQueryRequest,
        query_inventory_age: Callable[[str, date], InventoryAgeReportQueryResult]
        | None = None,
    ) -> InventoryAgeReportQueryResult:
        """Execute one immutable report request envelope."""
        if not isinstance(request, ReportQueryRequest):
            raise TypeError('Reports query requires ReportQueryRequest')
        if request.purchase_source_request is not None:
            if request.report_id != 'purchase-source-performance' or self._purchase_source_performance_query is None:
                raise KeyError(f'unsupported executable report: {request.report_id}')
            return self._purchase_source_performance_query.get_evidence_for_request(request.purchase_source_request)
        return self.query_inventory_age_report(request.report_id, request.inventory_age_request, query_inventory_age=query_inventory_age)

    def query_inventory_age_report(
        self,
        report_id: str,
        request: InventoryAgeReportQueryRequest,
        query_inventory_age: Callable[[str, date], InventoryAgeReportQueryResult]
        | None = None,
    ) -> InventoryAgeReportQueryResult:
        """Execute the only currently approved report through its query boundary."""
        if not isinstance(request, InventoryAgeReportQueryRequest):
            raise TypeError(
                'Inventory Age report query requires InventoryAgeReportQueryRequest'
            )
        normalized_report_id = str(report_id).strip().lower()
        self._catalog.get(normalized_report_id)
        if normalized_report_id != 'inventory-age-patterns':
            raise KeyError(f'unsupported executable report: {normalized_report_id}')
        if query_inventory_age is not None:
            return query_inventory_age(request.inventory_position_id, request.as_of_date)
        return self._inventory_age_query.get_inventory_age_for_request(request)
