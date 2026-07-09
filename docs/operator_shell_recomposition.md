# Operator Shell Recomposition

## First production slice

MarketDEX now separates Mission Control from the operational inventory and listing workspaces.

Mission Control is the business-at-a-glance entry point. It presents the existing authoritative snapshot values without duplicating business logic or persistence authority and gives the operator a clear next action into Inventory.

The existing Inventory & Pricing and Listing Workflow capabilities remain intact. Their services, repositories, SQLite authority, pricing calculations, listing plan state, marketplace package state, listing execution history, and sale completion boundaries are unchanged.

This slice intentionally changes composition before deeper workspace separation. The next recomposition slices can split Inventory from Pricing and Listing from Sales while preserving the same authority spine.
