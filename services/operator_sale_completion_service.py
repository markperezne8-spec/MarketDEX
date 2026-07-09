from core.event_repository import EventRepository
from repositories.asset_repository import AssetRepository
from repositories.inventory_repository import InventoryRepository
from services.marketplace_lifecycle_service import AuthorityBlocked, MarketplaceLifecycleService
from services.sales_service import SalesService


class OperatorSaleCompletionService:
    """Desktop orchestration only. Sales authority owns sale truth; lifecycle authority owns allocation consumption."""

    def __init__(self, database):
        self.database = database
        self.events = EventRepository()
        self.sales = SalesService(database, self.events, AssetRepository(), InventoryRepository())
        self.lifecycle = MarketplaceLifecycleService(database, self.events)

    def complete_sale(self, *, sale_request_id, conversion_request_id, sale_id, allocation_id,
                      sale_quantity, revenue_minor, marketplace_fees_minor, shipping_minor,
                      packaging_minor, evidence_reference, intent):
        if str(intent).strip().upper() != 'SOLD':
            raise AuthorityBlocked('Explicit SOLD sale request required')
        if not str(evidence_reference).strip():
            raise AuthorityBlocked('Marketplace sale evidence reference required')
        q = int(sale_quantity)
        money = [int(revenue_minor), int(marketplace_fees_minor), int(shipping_minor), int(packaging_minor)]
        if q <= 0 or money[0] <= 0 or any(value < 0 for value in money):
            raise AuthorityBlocked('Valid sale quantity and financial evidence required')
        with self.database.read_connection() as connection:
            allocation = connection.execute(
                "SELECT * FROM marketplace_publication_allocations WHERE allocation_id=? AND state='ACTIVE'",
                (allocation_id,),
            ).fetchone()
            if allocation is None:
                raise AuthorityBlocked('Active recorded listing required')
            remaining = int(allocation['allocated_quantity']) - int(allocation['released_quantity']) - int(allocation['cancelled_quantity']) - int(allocation['consumed_quantity'])
            if q > remaining:
                raise AuthorityBlocked('Sale quantity exceeds active listing allocation')
            inventory_before = int(connection.execute(
                'SELECT quantity FROM inventory_authority WHERE asset_id=?', (allocation['asset_id'],)
            ).fetchone()['quantity'])

        sale_event = self.sales.record_sale(
            request_id=sale_request_id,
            sale_id=sale_id,
            asset_id=allocation['asset_id'],
            quantity=q,
            revenue_minor=money[0],
            marketplace_fees_minor=money[1],
            shipping_minor=money[2],
            packaging_minor=money[3],
        )
        self.lifecycle.sold_conversion(
            request_id=conversion_request_id,
            allocation_id=allocation_id,
            sale_id=sale_id,
            sale_event_id=sale_event.event_id,
            marketplace=allocation['marketplace'],
            sale_quantity=q,
            intent='SOLD_CONVERSION',
        )
        with self.database.read_connection() as connection:
            inventory_after = int(connection.execute(
                'SELECT quantity FROM inventory_authority WHERE asset_id=?', (allocation['asset_id'],)
            ).fetchone()['quantity'])
            financial_count = int(connection.execute(
                'SELECT COUNT(*) n FROM sales_financial_history WHERE sale_id=?', (sale_id,)
            ).fetchone()['n'])
            sold = connection.execute(
                "SELECT 1 FROM publication_lifecycle_events WHERE allocation_id=? AND event_type='SOLD_CONVERSION' AND sale_id=?",
                (allocation_id, sale_id),
            ).fetchone()
        if inventory_after != inventory_before - q or financial_count != 1 or sold is None:
            raise RuntimeError('Operator sale completion authority verification failed')
        return sale_id
