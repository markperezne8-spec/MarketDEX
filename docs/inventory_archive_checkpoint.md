# Inventory Archive Checkpoint

Accepted parent merge SHA: `1da6f7d0290345d7c8ca1e766d94d8b74e580ac6`.

Mission Control exposes Archive Selected for one active inventory asset. Confirmation explicitly states that the asset leaves the active inventory view while event identity, inventory history, movements, inventory authority, and audit evidence remain preserved.

Archive appends an `INVENTORY_ASSET_ARCHIVED` authoritative event and verified archive audit, then transitions the active asset projection from `COMPLETED` to the schema-supported inactive `CANCELLED` state. Active inventory lists and Mission Control inventory totals include only `COMPLETED` assets. Archived assets cannot be adjusted or archived twice.

The protected M39-M165 authority spine remains unmodified. The cumulative archive gate runs the complete test suite before merge.