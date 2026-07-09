# MarketDEX OS Initial Domain Model

## Authority
This inventory is an implementation bridge from the workbook business specification. Field-level schemas must be derived and validated against the frozen specification before operational CRUD is enabled.

## Core Entities

### Inventory Item
A tracked business holding available for operational inventory workflows.

### Product
A catalog or registry definition for a Pokémon TCG card, sealed product, set, or other supported product concept.

### Collection Asset
A personally held collectible governed by collection workflows rather than sale inventory workflows.

### Purchase
An acquisition event that contributes evidence for ownership and cost basis.

### Sale
A disposition event that records sale-level business evidence.

### Platform
A marketplace or operating channel used by MarketDEX workflows.

### Settlement
A financial reconciliation record governed by settlement authority contracts.

### Allocation Group
A grouping boundary used to attribute settlement evidence according to workbook-defined allocation authority.

### Audit Event
An append-oriented record of significant business or system actions requiring preserved evidence.

## Initial Domain Order

1. Inventory
2. Product Registry
3. Collection
4. Purchase and Sale
5. Audit
6. Settlement
7. Allocation

## Constraint
Entity names in this document are conceptual. Database tables and Python models must not be finalized solely from this summary; implementation must preserve workbook traceability and documented authority boundaries.
