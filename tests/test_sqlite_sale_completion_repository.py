from datetime import datetime, timedelta, timezone
from pathlib import Path

from core.database_manager import DatabaseManager
from core.sale_completion import (
    SaleCompletionAvailable,
    SaleCompletionConflict,
    SaleCompletionQuery,
    SaleCompletionUnavailable,
)
from core.sale_completion_repository import SaleCompletionRepository
from core.sqlite_sale_completion_repository import (
    SaleCompletionAdapterDiagnostic,
    SqliteSalesSaleCompletionRepository,
)


NOW = datetime(2026, 7, 26, 20, 0, tzinfo=timezone.utc)


def database(tmp_path: Path) -> DatabaseManager:
    manager = DatabaseManager(tmp_path / "marketdex.sqlite3")
    manager.initialize()
    return manager


def insert_sale(
    manager: DatabaseManager,
    *,
    sale_id: str,
    asset_id: str,
    event_id: str,
    created_at: str,
    quantity: int = 1,
    state: str = "COMPLETED",
) -> None:
    with manager.transaction() as connection:
        connection.execute(
            """
            INSERT INTO sales (
                sale_id, asset_id, quantity, revenue_minor, marketplace_fees_minor,
                shipping_minor, packaging_minor, cogs_minor, profit_minor, state,
                created_event_id, created_at
            ) VALUES (?, ?, ?, 0, 0, 0, 0, 0, 0, ?, ?, ?)
            """,
            (sale_id, asset_id, quantity, state, event_id, created_at),
        )


def query(**overrides) -> SaleCompletionQuery:
    values = {
        "inventory_ids": ("asset-1",),
        "sale_ids": (),
        "as_of": NOW,
    }
    values.update(overrides)
    return SaleCompletionQuery(**values)


def test_adapter_satisfies_repository_protocol_and_returns_completed_sale(tmp_path):
    manager = database(tmp_path)
    insert_sale(
        manager,
        sale_id="sale-1",
        asset_id="asset-1",
        event_id="event-1",
        quantity=2,
        created_at=(NOW - timedelta(hours=1)).isoformat(),
    )
    adapter = SqliteSalesSaleCompletionRepository(manager)

    assert isinstance(adapter, SaleCompletionRepository)
    read = adapter.query_sale_completion(query())

    assert isinstance(read.result, SaleCompletionAvailable)
    assert tuple(item.sale_id for item in read.result.evidence) == ("sale-1",)
    assert read.result.evidence[0].completed_unit_quantity == 2
    assert read.result.coverage.source_systems == ("sqlite.sales",)


def test_adapter_preserves_sale_identity_and_completion_range(tmp_path):
    manager = database(tmp_path)
    inside = NOW - timedelta(hours=2)
    outside = NOW - timedelta(days=2)
    insert_sale(manager, sale_id="sale-inside", asset_id="asset-x", event_id="event-inside", created_at=inside.isoformat())
    insert_sale(manager, sale_id="sale-outside", asset_id="asset-x", event_id="event-outside", created_at=outside.isoformat())
    adapter = SqliteSalesSaleCompletionRepository(manager)

    read = adapter.query_sale_completion(
        query(
            inventory_ids=(),
            sale_ids=("sale-inside", "sale-outside"),
            completed_from=NOW - timedelta(hours=3),
            completed_until=NOW - timedelta(hours=1),
        )
    )

    assert isinstance(read.result, SaleCompletionAvailable)
    assert tuple(item.sale_id for item in read.result.evidence) == ("sale-inside",)


def test_complete_empty_read_is_available(tmp_path):
    adapter = SqliteSalesSaleCompletionRepository(database(tmp_path))

    read = adapter.query_sale_completion(query())

    assert isinstance(read.result, SaleCompletionAvailable)
    assert read.result.evidence == ()
    assert read.result.coverage.evidence_count == 0


def test_malformed_row_fails_closed_as_conflict(tmp_path):
    manager = database(tmp_path)
    insert_sale(
        manager,
        sale_id="sale-bad",
        asset_id="asset-1",
        event_id="event-bad",
        created_at="not-a-timestamp",
    )
    adapter = SqliteSalesSaleCompletionRepository(manager)

    read = adapter.query_sale_completion(query(as_of=NOW + timedelta(days=1)))

    assert isinstance(read.result, SaleCompletionConflict)
    assert read.result.reason_code == "sqlite_sales_row_decode_conflict"
    assert isinstance(read.diagnostic, SaleCompletionAdapterDiagnostic)
    assert read.diagnostic.row_identity == "sale-bad"


def test_source_failure_is_unavailable():
    class BrokenDatabaseManager:
        def read_connection(self):
            raise RuntimeError("offline")

    adapter = SqliteSalesSaleCompletionRepository(BrokenDatabaseManager())  # type: ignore[arg-type]

    read = adapter.query_sale_completion(query())

    assert isinstance(read.result, SaleCompletionUnavailable)
    assert read.result.reason_code == "sqlite_sales_read_unavailable"
