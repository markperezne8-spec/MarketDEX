# Market Intelligence Warehouse Executable Migration Guardrails

Build 700Y defines the guardrails required before MarketDEX adds any executable SQLite migration for the offline Market Intelligence warehouse.

This document is intentionally planning-only. It does not add SQL files, SQLite connections, migration runners, adapters, repository implementations, writes, imports, seed data, live providers, or UI changes.

## Ownership

Future executable migrations must be owned by the Market Intelligence warehouse infrastructure layer. They must not be owned by the Product Registry, inventory, listings, pricing, collection, reports, or UI modules.

The Product Registry remains the authority for product identity. A future warehouse migration may reference Product Registry identifiers, but it must not create, rename, merge, delete, or mutate Product Registry records.

Repository interfaces remain the boundary for application reads and writes. A future migration may prepare schema storage used by repository implementations, but it must not bypass repository contracts to mutate business-domain records.

## Required preflight checks

Before a future executable migration runs, it must verify all of the following conditions:

1. the target database path is explicit and local;
2. the database can be opened in offline mode without network access;
3. the current schema version is readable;
4. the current schema version is one of the supported source versions;
5. the requested target schema version is deterministic and newer than the current version;
6. the Product Registry schema and Market Intelligence warehouse schema are version-checked separately;
7. the migration plan contains only warehouse-owned tables and indexes;
8. no live provider, scraper, API credential, scheduler, alert, or cloud-sync dependency is required;
9. a backup or rollback strategy is available before any write begins;
10. dry-run validation succeeds before execution mode is allowed.

If any preflight check fails, the future migration must fail closed before performing writes.

## Dry-run expectations

A future migration runner must support dry-run mode before write mode. Dry-run mode must:

- inspect the existing schema version;
- build the ordered migration plan;
- validate source and target compatibility;
- report planned table and index changes;
- report unsupported versions explicitly;
- report whether a backup would be required;
- avoid opening a write transaction;
- avoid changing schema metadata;
- avoid inserting seed data;
- avoid mutating observations, provenance, snapshots, sources, preview history, Product Registry records, or business-domain records.

Dry-run output must be deterministic for the same input schema state.

## Idempotency expectations

Future executable migrations must be safe to evaluate repeatedly. The intended behavior is:

- re-running an already-applied migration should detect that no work is required;
- partially applied migrations must not be silently accepted;
- schema metadata must be written only after the migration transaction succeeds;
- duplicate tables, indexes, or seed rows must not be created;
- failed migration attempts must leave a clear failure state or roll back completely.

No migration may rely on wall-clock timing, live market data, network calls, or provider responses to decide whether it is complete.

## Transaction and rollback expectations

A future executable migration must use an explicit transaction for schema changes that belong to one migration step. If a step fails, MarketDEX must roll back that step rather than leaving a partially applied warehouse schema.

Rollback planning must include:

- backup location expectations;
- failure messages that name the failed migration step;
- schema-version state after rollback;
- preservation of existing non-warehouse data;
- no mutation of Product Registry authority records;
- no mutation of inventory, listings, collection, pricing, reports, or settings records.

## Failure reporting

Failures must be explicit and actionable. Future migration errors should report:

- current schema version;
- target schema version;
- failed preflight or migration step;
- whether writes had started;
- whether rollback completed;
- whether manual review is required.

Failure reporting must not expose secrets, tokens, provider credentials, or local filesystem details beyond the minimum local database path context needed for debugging.

## Non-goals for Build 700Y

Build 700Y does not introduce:

- SQL files;
- executable migrations;
- migration runners;
- SQLite connections;
- repository implementations;
- adapters;
- writes or imports;
- seed data;
- live providers;
- network calls;
- scraping;
- credentials;
- schedulers;
- alerts;
- cloud sync;
- UI changes;
- business-domain mutation authority.
