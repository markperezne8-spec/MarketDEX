from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository, ReplayRejected
from services.inventory_product_link_service import InventoryProductLinkService, ASSET
from services.marketplace_listing_readiness_service import MarketplaceListingReadinessService
from services.marketplace_lifecycle_service import MarketplaceLifecycleService
from services.product_sale_execution_service import (
    ProductSaleExecutionService, SALE_REQ, CONVERSION_REQ, SALE_ID,
)

ALLOCATION_ID = "ALLOC-M38-CHARIZARD-001"
PUBLICATION_REQ = "M38-ACCEPTANCE-PUBLICATION-001"


class M38AcceptanceService:
    def __init__(self, path):
        self.path = Path(path)
        self.sale = ProductSaleExecutionService(self.path)

    def _fixture(self):
        m35 = InventoryProductLinkService(self.path)
        m35_result = m35.run_acceptance()
        if m35_result["passed"] != 12:
            raise RuntimeError("M35 acceptance authority incomplete")
        pid = m35.ensure_acceptance_authority()
        link_id = m35_result["lid"]

        m36 = MarketplaceListingReadinessService(self.path)
        m36_result = m36.run_acceptance()
        if m36_result["passed"] != 12:
            raise RuntimeError("M36 acceptance authority incomplete")
        listing_id = m36.create_listing_identity(pid, "eBay", "M36-EBAY-CHARIZARD-001", "M36-LISTING-IDENTITY-001")

        db = DatabaseManager(self.path)
        db.initialize()
        m30 = MarketplaceLifecycleService(db, EventRepository())
        with db.read_connection() as c:
            existing = c.execute(
                "SELECT 1 FROM marketplace_publication_allocations WHERE allocation_id=?",
                (ALLOCATION_ID,),
            ).fetchone()
        if not existing:
            m30.list_publication(
                request_id=PUBLICATION_REQ,
                allocation_id=ALLOCATION_ID,
                asset_id=ASSET,
                marketplace="eBay",
                requested_allocation_quantity=2,
                publication_reference="M36-EBAY-CHARIZARD-001",
                publication_identity=listing_id,
                evidence_type="M36_READY_LISTING",
                evidence_reference=listing_id,
                evidence_complete=True,
                intent="LISTED",
            )
        return pid, link_id, listing_id

    def execute(self):
        pid, link_id, listing_id = self._fixture()
        kwargs = dict(
            sale_request_id=SALE_REQ,
            conversion_request_id=CONVERSION_REQ,
            sale_id=SALE_ID,
            product_id=pid,
            asset_id=ASSET,
            inventory_product_link_id=link_id,
            listing_id=listing_id,
            allocation_id=ALLOCATION_ID,
            marketplace="eBay",
            sale_quantity=2,
            revenue_minor=5000,
            marketplace_fees_minor=650,
            shipping_minor=100,
            packaging_minor=50,
            evidence_type="MARKETPLACE_SALE_EVIDENCE",
            evidence_reference="M38-EBAY-SALE-EVIDENCE-001",
            evidence_complete=True,
            intent="SOLD",
        )
        self.sale.execute_sold(**kwargs)

        try:
            with self.sale.db.read_connection() as c:
                sale = c.execute("SELECT created_event_id FROM sales WHERE sale_id=?", (SALE_ID,)).fetchone()
            self.sale.m30.sold_conversion(
                request_id=CONVERSION_REQ,
                allocation_id=ALLOCATION_ID,
                sale_id=SALE_ID,
                sale_event_id=sale["created_event_id"],
                marketplace="eBay",
                sale_quantity=2,
                intent="SOLD_CONVERSION",
            )
        except ReplayRejected:
            pass
        else:
            raise RuntimeError("M30 conversion replay was not blocked")

        self.sale.execute_sold(**kwargs)
        return self.verify()

    def verify(self):
        return self.sale.verify(
            allocation_id=ALLOCATION_ID,
            sale_id=SALE_ID,
            sale_request_id=SALE_REQ,
            conversion_request_id=CONVERSION_REQ,
        )
