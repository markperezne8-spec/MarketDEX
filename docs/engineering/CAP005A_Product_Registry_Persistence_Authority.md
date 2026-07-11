# CAP-005A — Product Registry Persistence Authority

CAP-005A reconciles the existing Product Registry service with MarketDEX's permanent SQLite runtime authority.

The canonical owner of Product Registry persistence is `core/schema.py` schema version 24. `ProductRegistryService` consumes that schema through `DatabaseManager`; it must not create private copies of shared event, replay, or audit tables.

The accepted replay identity is reconstructed from immutable `event_identity.request_id` authority and the Product Registry row linked by `created_event_id`. Product registration and alias audit evidence use the canonical `audit_events` contract.

This boundary does not introduce Product Registry UI, catalog imports, or external APIs. Those require separate classification after persistence authority is merged and verified.