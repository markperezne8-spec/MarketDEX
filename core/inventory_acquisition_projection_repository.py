from __future__ import annotations

from typing import Protocol, runtime_checkable

from core.inventory_acquisition_projection import (
    InventoryAcquisitionProjectionRequest,
    InventoryAcquisitionProjectionResult,
)


@runtime_checkable
class InventoryAcquisitionProjectionRepository(Protocol):
    def read_inventory_acquisition_projection(
        self, request: InventoryAcquisitionProjectionRequest,
    ) -> InventoryAcquisitionProjectionResult: ...
