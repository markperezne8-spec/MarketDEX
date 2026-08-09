from __future__ import annotations

from dataclasses import dataclass

from reports.inventory_age_query_request import InventoryAgeReportQueryRequest
from reports.purchase_source_performance_contract import PurchaseSourcePerformanceRequest


@dataclass(frozen=True, slots=True)
class ReportQueryRequest:
    """Immutable request envelope for one catalog-approved report query."""

    report_id: str
    inventory_age_request: InventoryAgeReportQueryRequest | None = None
    purchase_source_request: PurchaseSourcePerformanceRequest | None = None

    def __post_init__(self) -> None:
        normalized_report_id = str(self.report_id).strip().lower()
        if not normalized_report_id:
            raise ValueError('report_id is required')
        payloads = (self.inventory_age_request, self.purchase_source_request)
        if sum(value is not None for value in payloads) != 1:
            raise ValueError('ReportQueryRequest requires exactly one report request payload')
        if self.inventory_age_request is not None and not isinstance(self.inventory_age_request, InventoryAgeReportQueryRequest):
            raise TypeError('inventory_age_request must be InventoryAgeReportQueryRequest')
        if self.purchase_source_request is not None and not isinstance(self.purchase_source_request, PurchaseSourcePerformanceRequest):
            raise TypeError('purchase_source_request must be PurchaseSourcePerformanceRequest')
        object.__setattr__(self, 'report_id', normalized_report_id)
