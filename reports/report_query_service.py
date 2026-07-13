from __future__ import annotations

from reports.definitions import ReportCatalog
from reports.inventory_age_query import (
    InventoryAgeReportQueryResult,
    InventoryAgeReportQueryService,
)
from reports.inventory_age_query_request import InventoryAgeReportQueryRequest


class ReportQueryService:
    """Routes catalog-approved report requests to read-only query services."""

    def __init__(
        self,
        catalog: ReportCatalog,
        inventory_age_query: InventoryAgeReportQueryService,
    ) -> None:
        self._catalog = catalog
        self._inventory_age_query = inventory_age_query

    def query_inventory_age_report(
        self,
        report_id: str,
        request: InventoryAgeReportQueryRequest,
    ) -> InventoryAgeReportQueryResult:
        """Execute the only currently approved report through its query boundary."""
        normalized_report_id = str(report_id).strip().lower()
        self._catalog.get(normalized_report_id)
        if normalized_report_id != 'inventory-age-patterns':
            raise KeyError(f'unsupported executable report: {normalized_report_id}')
        return self._inventory_age_query.get_inventory_age_for_request(request)
