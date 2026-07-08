# Inventory Edit Details Checkpoint

Accepted parent merge SHA: `1a614c83bc5faa2dbcf3f309913af1b1cbcd9093`.

Mission Control exposes Edit Details for one active inventory asset. The workflow corrects asset name and supported asset type through an `INVENTORY_ASSET_DETAILS_EDITED` event and verified `INVENTORY_DETAILS_EDIT` audit.

Quantity, cost, inventory authority, inventory history, and inventory movements are not mutated by a detail correction. Archived assets cannot be edited. No-op edits and unsupported types are rejected.

The protected M39-M165 authority spine remains unmodified. The dedicated gate verifies the edit contract together with archive, restore, Mission Control, and the cumulative protected authority spine.