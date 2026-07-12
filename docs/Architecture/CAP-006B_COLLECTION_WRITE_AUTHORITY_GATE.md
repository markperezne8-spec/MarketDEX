# CAP-006B — Collection Write-Authority Gate

**Status:** PLAN — authority gate; mutation remains blocked  
**Capability:** CAP-006 Collection  
**Requirement:** REQ-COL-001  
**Issue:** #177  
**Runtime baseline:** `main` after PR #175

## Decision

MarketDEX may expose the merged read-only Collection Position projection, but it must not create Collection-owned persistence, CRUD, lifecycle commands, inferred classification, or valuation behavior until the business authority listed in this document is approved and traceable.

The current Collection Overview is a query surface over existing Product Registry and Inventory authority. It is not proof that a complete Collection ownership model exists.

## Current approved read contract

`CollectionPositionService` may return a deterministic, bounded, zero-mutation projection containing:

- canonical `product_id` from Product Registry authority;
- linked `asset_id` from the canonical inventory-product linkage;
- canonical product name and product type;
- inventory quantity;
- storage location or custody evidence already recorded by Inventory;
- acquisition date and acquisition source evidence already recorded by Inventory;
- explicit absence of Collection-owned condition, grade, and collector intent.

These values are references or projections over existing authorities. They are not independently mutable Collection facts.

## Authority separation

### Product Registry owns

- canonical product identity;
- product naming and type;
- set, card-number, variant, alias, and catalog identity semantics.

Collection must reference `product_id`; it must not create a second catalog.

### Inventory owns

- business-held asset identity;
- sellable or operational quantity;
- inventory cost and business acquisition details;
- storage evidence currently recorded for business inventory;
- inventory-product linkage;
- listing, reservation, sale, and settlement-related business workflows.

Collection must not mutate Inventory status or reuse an Inventory status field as collector intent.

### Collection may eventually own

Only after explicit workbook/business approval:

- stable Collection Position identity;
- collector-intent facts and transitions;
- Collection-specific custody or location facts, when distinct from Inventory;
- Collection-specific acquisition or provenance evidence, when distinct from Inventory;
- condition and grading evidence under an approved evidence model;
- Collection lifecycle and archive semantics.

## Blocked authority decisions

The following decisions remain **BLOCKED** and must not be invented in code, schema, tests, or UI:

1. **Position grain and identity** — whether a Collection Position is per product, physical item, lot, graded certification, or another approved grain.
2. **Ownership lifecycle** — allowed acquire, adjust, transfer, split, merge, archive, and restore transitions.
3. **Collector-intent vocabulary** — favorites, never-sell, willing-to-trade, willing-to-sell, goals, wishlist, or other values.
4. **Condition and grading evidence** — source, verifier, certification identity, revision, conflict, and supersession rules.
5. **Provenance and custody** — evidence ownership and whether existing Inventory fields are sufficient or only provisional display data.
6. **Inventory relationship** — coexistence, transfer, or conversion semantics between Collection and Inventory Positions.
7. **Deletion semantics** — archive, tombstone, reversal, and immutable-history expectations.
8. **Cost and valuation** — whether cost is referenced evidence, duplicated evidence, derived data, or outside Collection; all market valuation remains outside this gate.
9. **Event model** — event names, payloads, replay behavior, idempotency keys, and audit expectations.
10. **Migration and rollback** — schema version, backfill rules, fail-closed behavior, and rollback guarantees.

## Provisional command boundary

The following names describe planning concepts only. They are not approved interfaces and must not be implemented until their fields and preconditions are accepted:

- acquire a Collection Position;
- adjust Collection quantity;
- transfer between Inventory and Collection;
- record or revise collector intent;
- record condition or grading evidence;
- archive or restore a Collection Position.

No implementation may infer approval merely because a command appears in this planning document.

## Query guarantees

All CAP-006 query paths must:

- use read-only database access;
- preserve Product Registry and Inventory rows exactly;
- return deterministic ordering;
- validate and bound result limits;
- produce explicit empty and unmatched states;
- survive process restart using existing canonical authority;
- display absent Collection facts as absent or `Not recorded`;
- never infer condition, grade, intent, valuation, market price, profit, or portfolio classification.

## Event, audit, and persistence expectations

Before mutation enters BUILD, the approved design must specify:

- one canonical Collection persistence owner;
- append-only domain-event and audit behavior;
- replay-safe and idempotent command processing;
- restart reconstruction expectations;
- transaction boundaries with Product Registry and Inventory references;
- conflict behavior for stale or contradictory evidence;
- immutable history preservation for revisions and archive operations;
- fail-closed behavior when authority or linkage is missing.

CAP-006 must extend the existing runtime SQLite and audit architecture. It must not create a second database authority or parallel audit system.

## Acceptance gate for CAP-006C

A later CAP-006C mutation build may begin only when all of the following exist in the repository:

- approved workbook/business field vocabulary;
- approved Collection Position grain and stable identity rules;
- approved Inventory relationship and transition rules;
- approved condition, grading, intent, provenance, and archive ownership decisions;
- command, query, event, repository, and transaction contracts;
- schema migration, replay, restart, rollback, and idempotency expectations;
- tests proving authority separation and zero unintended mutation;
- updated Capability Matrix and Requirements Traceability Matrix;
- a separately scoped GitHub issue and branch.

Until every gate is satisfied, CAP-006 remains `Partial`, and the read-only Collection Overview is the maximum approved runtime behavior.

## Non-goals

- Collection CRUD or persistence;
- speculative enums or status fields;
- automatic Inventory-to-Collection conversion;
- valuation, profit, Portfolio, or Reports logic;
- grading workflow automation;
- wishlist automation;
- external catalog or market-data integration;
- cloud synchronization;
- replacement of Product Registry, Inventory, audit, or runtime database authority.
