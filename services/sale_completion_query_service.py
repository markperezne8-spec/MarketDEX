from __future__ import annotations

from datetime import datetime

from core.sale_completion import SaleCompletionQuery
from core.sale_completion_repository import (
    SaleCompletionRepository,
    SaleCompletionRepositoryRead,
)


class SaleCompletionQueryService:
    """Application-service seam for deterministic sale-completion reads."""

    def __init__(self, repository: SaleCompletionRepository) -> None:
        self._repository = repository

    def query(
        self,
        *,
        inventory_ids: tuple[str, ...] = (),
        sale_ids: tuple[str, ...] = (),
        as_of: datetime,
        completed_from: datetime | None = None,
        completed_until: datetime | None = None,
    ) -> SaleCompletionRepositoryRead:
        query = SaleCompletionQuery(
            inventory_ids=inventory_ids,
            sale_ids=sale_ids,
            as_of=as_of,
            completed_from=completed_from,
            completed_until=completed_until,
        )
        return self._repository.query_sale_completion(query)
