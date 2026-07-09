# Operator Workspace Recomposition

MarketDEX keeps the existing offline SQLite authority and business services intact while progressively reducing the long vertical operator workflow.

## Current boundary

The desktop shell now presents four operator workspaces:

1. Mission Control — business snapshot and next action.
2. Inventory & Pricing — inventory selection, intake, cost, and pricing decisions.
3. Listings — listing plan, preparation, review, and approved package handoff.
4. Sales — marketplace listing outcomes and confirmed sale completion.

The Sales workspace is intentionally separated from Listings because recording a marketplace outcome and confirming a sold transaction are post-listing operator work. No database, inventory, pricing, listing, or sale authority semantics change in this recomposition.

## Next boundary

Separate Inventory and Pricing into focused workspaces without duplicating widgets or bypassing the selected-asset authority flow.
