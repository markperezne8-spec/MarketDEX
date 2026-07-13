# Build 700S — Market Intelligence Warehouse Schema Prebuild

## Purpose

Build 700S defines a proposed future SQLite schema plan for the offline Market Intelligence warehouse without implementing schema, migrations, repositories, or writes yet.

This build is planning-only. It records the intended table boundaries so a later persistence build can be explicit, reviewable, and safe.

## Relationship to Build 700R

Build 700R established that a future Market Intelligence warehouse must remain offline-first, source-attributed, provenance-visible, and separate from live provider execution.

Build 700S narrows that boundary into candidate tables and ownership expectations while preserving the same non-persistence rule for this build.

## Candidate future tables

A later explicit persistence build may introduce tables equivalent to the following concepts:

### `market_observations`

Stores normalized offline market evidence rows.

Expected fields may include:

- observation id;
- product id reference;
- source id reference;
- observation kind;
- observed value;
- currency;
- confidence;
- sample size;
- observed-at timestamp;
- ingested-at timestamp;
- metadata payload.

Authority requirements:

- product identity must reference Product Registry authority;
- observation rows must remain evidence records, not valuation authority;
- observation writes must come only through an explicit warehouse repository or import boundary in a later build.

### `market_sources`

Stores source/provider provenance records.

Expected fields may include:

- source id;
- source name;
- source type;
- fixture dataset version;
- offline/import marker;
- provenance notes.

Authority requirements:

- source records must be visible to readers;
- no credential, live provider, scraping, or network authority may be inferred from a stored source.

### `market_snapshots`

Stores offline snapshot batches for grouped market evidence.

Expected fields may include:

- snapshot id;
- source id reference;
- snapshot label;
- captured-at timestamp;
- imported-at timestamp;
- fixture dataset version;
- provenance notes.

Authority requirements:

- snapshots must be deterministic and source-attributed;
- snapshots must not trigger refreshes, schedulers, alerts, or automation.

### `market_snapshot_observations`

Links snapshots to normalized observations.

Expected fields may include:

- snapshot id reference;
- observation id reference;
- row order;
- derivation notes.

Authority requirements:

- links must preserve evidence traceability;
- links must not duplicate business-domain records or mutate product/listing/inventory data.

### `saved_query_preview_history`

Stores read-only saved-query preview results derived from persisted observations.

Expected fields may include:

- preview id;
- query id;
- observation id reference;
- product id reference;
- previewed-at timestamp;
- preview label;
- derivation notes.

Authority requirements:

- saved research query definitions must remain separate from warehouse observation storage;
- preview history must remain read-only and evidence-backed;
- preview history must not become executable query scheduling or automation authority.

## Explicit non-goals for Build 700S

Build 700S must not:

- create database schema, migrations, repositories, or SQLite writes;
- add seed data, importers, adapters, or fixture loaders;
- persist saved research query definitions or preview results;
- execute live marketplace queries;
- call network providers, scraping services, credentials, cloud sync, alerts, timers, or schedulers;
- add editing, import, delete, run, refresh, or automation controls;
- mutate inventory, listings, pricing, product registry, collection, or any business-domain record.

## Future implementation gate

The first actual warehouse persistence build must verify:

- schema ownership is explicit and migration-backed;
- all records are source-attributed and timestamped;
- product references preserve Product Registry authority;
- saved query definitions remain separate from observation storage;
- preview history remains read-only;
- no live provider, network, scheduler, automation, valuation, or business-domain mutation authority is introduced;
- CI covers schema boundaries and no-op behavior before any UI exposure.

## Visual verification

Not required for Build 700S because this build is documentation/test-only.

A future build that changes Market Intelligence UI, database-backed behavior, import behavior, or warehouse-visible data will require visual verification.
