from __future__ import annotations

from typing import cast

from core.database_manager import DatabaseManager
from core.sale_completion_repository import SaleCompletionRepository
from core.sale_completion_repository_registration import register_sale_completion_repository
from core.sqlite_sale_completion_repository import SqliteSalesSaleCompletionRepository


def test_registration_constructs_sqlite_repository_with_owned_database_manager() -> None:
    database_manager = cast(DatabaseManager, object())

    repository = register_sale_completion_repository(database_manager)

    assert isinstance(repository, SqliteSalesSaleCompletionRepository)
    assert isinstance(repository, SaleCompletionRepository)
    assert repository._database_manager is database_manager
