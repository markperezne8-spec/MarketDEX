from __future__ import annotations

from dataclasses import dataclass

from reports.inventory_age_query_request import InventoryAgeReportQueryRequest


@dataclass(frozen=True, slots=True)
class ReportQueryRequest:
    """Immutable request envelope for one catalog-approved report query."""

    report_id: str
    inventory_age_request: InventoryAgeReportQueryRequest

    def __post_init__(self) -> None:
        normalized_report_id = str(self.report_id).strip().lower()
        if not normalized_report_id:
            raise ValueError('report_id is required')
        if not isinstance(
            self.inventory_age_request,
            InventoryAgeReportQueryRequest,
        ):
            raise TypeError(
                'ReportQueryRequest requires InventoryAgeReportQueryRequest'
            )
        object.__setattr__(self, 'report_id', normalized_report_id)
