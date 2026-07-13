from datetime import date

from reports.inventory_age_query import (
    INPUT_NOT_FOUND,
    InventoryAgeReportQueryResult,
    InventoryAgeReportQueryService,
)
from reports.inventory_age_query_request import InventoryAgeReportQueryRequest


class _Provider:
    def __init__(self) -> None:
        self.calls = []

    def get_inventory_age_input(self, position_id: str, as_of: date):
        self.calls.append((position_id, as_of))
        return InventoryAgeReportQueryResult(INPUT_NOT_FOUND, reason='no approved evidence')


def test_build701ag_request_entrypoint_preserves_one_provider_call() -> None:
    provider = _Provider()
    service = InventoryAgeReportQueryService(provider)
    request = InventoryAgeReportQueryRequest(' position-701ag ', date(2026, 7, 13))

    result = service.get_inventory_age_for_request(request)

    assert result.outcome == INPUT_NOT_FOUND
    assert provider.calls == [('position-701ag', date(2026, 7, 13))]
