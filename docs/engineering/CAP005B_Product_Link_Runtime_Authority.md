# CAP-005B — Product-Link Runtime Authority

CAP-005B consolidates the existing inventory-to-product linkage and marketplace listing-readiness persistence with the permanent SQLite runtime authority.

`core/schema.py` schema version 26 owns the product-link, listing-identity, and publication-readiness tables and their append-only history triggers. `InventoryProductLinkService` and `MarketplaceListingReadinessService` initialize and transact through `DatabaseManager`; neither service may create a private copy of shared event, replay, audit, product, inventory, allocation, or product-link tables.

The boundary preserves the existing M35/M36 behavior: explicit product linkage, one-product-per-asset conflict defense, quantity/readiness derivation, replay defense, immutable history, and restart reconstruction. It does not introduce a Product Registry operator UI, catalog import, external API, or new marketplace allocation authority.
