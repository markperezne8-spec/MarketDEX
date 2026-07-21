from __future__ import annotations

from typing import Protocol, runtime_checkable

from reports.inventory_turnover_contract import (
    OUTCOME_UNAVAILABLE,
    InventoryTurnoverReportRequest,
    InventoryTurnoverReportResult,
)

_UNAVAILABLE_SOURCE_DOMAINS = ('audit', 'inventory', 'listing')
_UNAVAILABLE_SOURCE_COVERAGE = ('unavailable',)
_UNAVAILABLE_EVIDENCE_STATE = 'unavailable'
_UNAVAILABLE_PROVENANCE = ('inventory-turnover-query-boundary:provider-unavailable',)


@runtime_checkable
class InventoryTurnoverReportProvider(Protocol):
    """Read-only boundary for future Inventory Turnover report evidence."""

    def get_inventory_turnover_result(
        self,
        request: InventoryTurnoverReportRequest,
    ) -> InventoryTurnoverReportResult:
        """Return one immutable Inventory Turnover result without mutation."""


class InventoryTurnoverReportQueryService:
    """Injected query boundary around an Inventory Turnover result provider.

    This service owns no source reads and performs no formula calculation. It only
    preserves the approved request/result contract and fails closed when the
    injected provider cannot return a valid immutable report result.
    """

    def __init__(self, provider: InventoryTurnoverReportProvider) -> None:
        self._provider = provider

    def get_inventory_turnover_for_request(
        self,
        request: InventoryTurnoverReportRequest,
    ) -> InventoryTurnoverReportResult:
        """Return an immutable report result for one validated request."""
        if not isinstance(request, InventoryTurnoverReportRequest):
            raise TypeError('request must be an InventoryTurnoverReportRequest')

        try:
            provider_result = self._provider.get_inventory_turnover_result(request)
        except Exception:
            return self._unavailable_result(
                request,
                'Inventory Turnover provider unavailable',
            )

        if not isinstance(provider_result, InventoryTurnoverReportResult):
            return self._unavailable_result(
                request,
                'Inventory Turnover provider returned unsupported result',
            )

        return provider_result

    @staticmethod
    def _unavailable_result(
        request: InventoryTurnoverReportRequest,
        reason: str,
    ) -> InventoryTurnoverReportResult:
        return InventoryTurnoverReportResult(
            request=request,
            outcome=OUTCOME_UNAVAILABLE,
            reason=reason,
            source_domains=_UNAVAILABLE_SOURCE_DOMAINS,
            source_coverage=_UNAVAILABLE_SOURCE_COVERAGE,
            evidence_state=_UNAVAILABLE_EVIDENCE_STATE,
            provenance=_UNAVAILABLE_PROVENANCE,
        )
