from __future__ import annotations

from datetime import datetime, time, timezone
from typing import Protocol, runtime_checkable

from core.inventory_acquisition_projection import (
    InventoryAcquisitionProjectionAvailable,
    InventoryAcquisitionProjectionConflict,
    InventoryAcquisitionProjectionRequest,
    InventoryAcquisitionProjectionUnavailable,
)
from core.inventory_acquisition_projection_repository import InventoryAcquisitionProjectionRepository
from reports.purchase_source_performance_provider import (
    PurchaseSourcePerformanceInventoryRead,
    PurchaseSourcePerformanceInventoryReadRequest,
    PurchaseSourcePerformanceInventoryRecord,
)

UTC = timezone.utc


@runtime_checkable
class InventoryAcquisitionProjectionReader(Protocol):
    def read_inventory_acquisition_projection(self, request: InventoryAcquisitionProjectionRequest): ...


class PurchaseSourcePerformanceInventoryAdapter:
    """Maps canonical acquisition projection reads into the report reader seam."""

    def __init__(self, projection_repository: InventoryAcquisitionProjectionReader) -> None:
        if not isinstance(projection_repository, InventoryAcquisitionProjectionRepository):
            raise TypeError('projection_repository must implement InventoryAcquisitionProjectionRepository')
        self._projection_repository = projection_repository

    def read_purchase_source_performance_inventory(
        self, request: PurchaseSourcePerformanceInventoryReadRequest,
    ) -> PurchaseSourcePerformanceInventoryRead:
        if not isinstance(request, PurchaseSourcePerformanceInventoryReadRequest):
            raise TypeError('request must be a PurchaseSourcePerformanceInventoryReadRequest')
        projection_request = InventoryAcquisitionProjectionRequest(
            period_start=request.period_start,
            period_end=request.period_end,
            as_of=datetime.combine(request.as_of, time.max, tzinfo=UTC),
        )
        try:
            result = self._projection_repository.read_inventory_acquisition_projection(projection_request)
        except Exception:
            return PurchaseSourcePerformanceInventoryRead('unavailable', reason='inventory acquisition projection unavailable')
        if isinstance(result, InventoryAcquisitionProjectionUnavailable):
            return PurchaseSourcePerformanceInventoryRead('unavailable', reason=result.diagnostic.reason_code)
        if isinstance(result, InventoryAcquisitionProjectionConflict):
            return PurchaseSourcePerformanceInventoryRead('conflicting', reason=result.diagnostic.reason_code)
        if not isinstance(result, InventoryAcquisitionProjectionAvailable):
            return PurchaseSourcePerformanceInventoryRead('unavailable', reason='unsupported inventory acquisition projection')
        try:
            records = tuple(
                PurchaseSourcePerformanceInventoryRecord(
                    inventory_id=item.inventory_id,
                    acquired_units=item.acquired_units,
                    acquisition_date=item.acquisition_date,
                    purchase_source_label=item.purchase_source_label,
                )
                for item in result.records
            )
        except (TypeError, ValueError):
            return PurchaseSourcePerformanceInventoryRead('conflicting', reason='malformed inventory acquisition projection')
        return PurchaseSourcePerformanceInventoryRead('available', records, reason='complete canonical inventory acquisition coverage')
