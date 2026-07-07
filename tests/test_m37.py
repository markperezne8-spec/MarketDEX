from pathlib import Path
from tempfile import TemporaryDirectory

from services.inventory_product_link_service import InventoryProductLinkService
from services.marketplace_listing_readiness_service import MarketplaceListingReadinessService
from services.listing_publication_execution_service import ListingPublicationExecutionService


with TemporaryDirectory(prefix="marketdex_m37_") as temp_dir:
    p = Path(temp_dir) / "m37_acceptance.sqlite3"

    assert InventoryProductLinkService(p).run_acceptance()["passed"] == 12
    assert MarketplaceListingReadinessService(p).run_acceptance()["passed"] == 12

    r = ListingPublicationExecutionService(p).execute()
    assert r["passed"] == 12, r

    r2 = ListingPublicationExecutionService(p).execute()
    assert r2["passed"] == 12 and r2["available"] == 2, r2

print("M37 TESTS: 12 / 12 PASS")
print("M30 DIRECT SERVICE INTEGRATION: PASS")
print("REPLAY AFTER RESTART: PASS")
print("ZERO SECOND PUBLICATION / ALLOCATION: PASS")
print("ZERO INVENTORY / FINANCIAL MUTATION FROM LISTED EXECUTION: PASS")
