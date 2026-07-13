# Build 700W — Market Intelligence SQLite Adapter Boundary Prebuild

## Purpose

Build 700W defines the future SQLite adapter boundary for the offline Market Intelligence warehouse without implementing SQLite connections, SQL, schema, migrations, repository adapters, or database writes.

The future adapter must remain offline-first, repository-interface driven, provenance-preserving, and separate from Product Registry and business-domain mutation authority.

## Adapter ownership

A future SQLite adapter may eventually own:

- SQLite connection acquisition for the Market Intelligence warehouse only;
- explicit transaction scopes for future write operations;
- schema-version compatibility checks before reads or writes;
- deterministic row-to-domain mapping for warehouse models;
- database error translation into application-level failures;
- stable ordering for all read results.

A future SQLite adapter must not own:

- canonical product identity decisions;
- live provider execution;
- saved query execution authority;
- UI behavior or widget state;
- inventory, listing, pricing, Product Registry, collection, or other business-domain writes.

## Future write expectations

Future SQLite writes must be append-oriented and must:

- preserve original observation identifiers, timestamps, source attribution, and provenance references;
- use explicit transactions for multi-row operations;
- commit atomically or roll back completely;
- be idempotent for repeated ingestion attempts;
- reject conflicting duplicate identifiers instead of rewriting history in place;
- store canonical Product Registry product IDs as references only;
- keep snapshot membership immutable after creation.

## Future read expectations

Future SQLite reads must:

- return immutable warehouse domain models instead of raw rows;
- apply deterministic ordering for observations, snapshots, sources, provenance, and preview history;
- support repository interface filters without leaking SQL details to callers;
- preserve source and provenance visibility;
- avoid live provider calls, valuation authority, schedulers, alerts, or automation;
- keep saved-query preview history read-only.

## Failure behavior

A future adapter must fail explicitly when:

- the schema version is unknown or unsupported;
- required source or provenance references are missing;
- duplicate identifiers conflict with existing persisted facts;
- row values cannot be mapped into Build 700T immutable warehouse domain models;
- a transaction cannot be committed safely.

Failures must not partially mutate warehouse records or business-domain records.

## Relationship to repository interfaces

The future SQLite adapter must implement repository interfaces from the Market Intelligence warehouse boundary rather than being called directly by UI code.

Application services must remain the entry point for repository use. UI components must not own database connections, transaction authority, schema decisions, or import behavior.

## Explicit non-goals for this prebuild

Build 700W must not:

- add SQLite connections, SQL statements, schema, migrations, adapters, or repository implementations;
- write, import, seed, or persist records;
- execute live providers, network calls, scraping, credentials, alerts, schedulers, or cloud sync;
- add UI controls or user-visible behavior;
- mutate inventory, listings, pricing, Product Registry, collection, or other business-domain records.

## Visual verification

Not required for Build 700W because this build is documentation/test-only.
