# Build 700W — Market Intelligence SQLite Adapter Boundary Prebuild

## Purpose

Build 700W defines the future SQLite adapter boundary for the offline Market Intelligence warehouse without implementing SQLite connections, SQL, schema, migrations, adapters, repositories, or database writes.

## Adapter ownership

A future SQLite adapter must own:

- opening and closing warehouse database connections;
- explicit transaction boundaries for write operations;
- schema-version compatibility checks;
- deterministic conversion between SQLite rows and immutable warehouse domain models;
- translation of database failures into explicit repository-layer errors.

Application services and UI code must not own SQL, connections, transactions, row mapping, or migration authority.

## Future write behavior

A future adapter may implement the repository interfaces only after a separate approved persistence build.

Future writes must:

- preserve append-only observation and snapshot history;
- preserve original observation, capture, and provenance timestamps;
- preserve canonical Product Registry product IDs as references only;
- use idempotency keys or stable identifiers for repeated ingestion attempts;
- reject conflicting duplicate identifiers;
- commit related source, provenance, observation, and snapshot records atomically;
- roll back the complete transaction when any required write fails;
- avoid rewriting historical facts in place.

## Future read behavior

Future reads must:

- return immutable warehouse domain models;
- use deterministic ordering for observations, sources, provenance, snapshots, and preview history;
- preserve exact source attribution and provenance links;
- remain offline and read-only;
- avoid live-provider execution, valuation authority, or business-domain mutation.

## Schema and migration boundary

A later explicit build must define:

- the first SQLite schema version;
- table and index ownership;
- foreign-key enforcement;
- migration ordering and rollback policy;
- compatibility behavior for older databases;
- backup requirements before destructive migration steps.

Build 700W does not authorize any schema or migration implementation.

## Failure behavior

A future adapter must fail explicitly when:

- the schema version is unsupported;
- required identifiers or foreign references are missing;
- duplicate identifiers conflict with stored facts;
- transaction commit fails;
- row data cannot be mapped to a valid immutable domain model.

Failures must not silently drop records, partially commit related writes, or mutate another MarketDEX business domain.

## Explicit non-goals

Build 700W must not add:

- SQLite connections, SQL statements, tables, indexes, schema, or migrations;
- repository adapter or implementation code;
- imports, seed data, fixture persistence, or preview-history writes;
- live providers, network calls, scraping, credentials, alerts, schedulers, or cloud sync;
- UI changes or user-visible controls;
- mutation authority over inventory, listings, pricing, Product Registry, collection, or other business records.

## Visual verification

Not required because Build 700W is documentation/test-only.
