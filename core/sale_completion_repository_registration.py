from __future__ import annotations

from core.database_manager import DatabaseManager
from core.sale_completion_repository import SaleCompletionRepository
from core.sqlite_sale_completion_repository import SqliteSalesSaleCompletionRepository


def register_sale_completion_repository(
    database_manager: DatabaseManager,
) -> SaleCompletionRepository:
    """Construct the runtime sale-completion repository from the owned database manager."""
    return SqliteSalesSaleCompletionRepository(database_manager)
