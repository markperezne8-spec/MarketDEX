# Inventory Restore Checkpoint

Accepted parent merge SHA: `90ac5183b5c7e9a011a2a7ddbcf75d1ba2529c3d`.

Mission Control can switch between active and archived inventory projections. One archived asset can be selected and restored to active inventory through a visible confirmation workflow.

Restore appends an `INVENTORY_ASSET_RESTORED` authoritative event and a verified `INVENTORY_RESTORE` audit before transitioning the schema-supported asset state from `CANCELLED` to `COMPLETED`. Existing quantity, total cost, inventory authority, history, and movements remain preserved. Active assets cannot be restored and a restored asset cannot be restored twice without a new archive transition.

The protected M39-M165 authority spine remains unmodified. The restore gate verifies restore/archive contracts, Mission Control projection, and the cumulative protected authority spine.