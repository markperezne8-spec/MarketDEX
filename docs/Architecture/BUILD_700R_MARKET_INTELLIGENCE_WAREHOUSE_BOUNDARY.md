# Build 700R — Market Intelligence Warehouse Boundary Prebuild

## Purpose

Build 700R defines the boundary for a future offline Market Intelligence warehouse without implementing persistence yet.

The future warehouse may store normalized offline market observations, snapshots, source provenance, and read-only preview history. It must not become live-provider execution authority, valuation authority, automation authority, or a business-domain mutation path.

## Required authority model

A future warehouse implementation must:

- remain offline-first and deterministic by default;
- store only source-attributed market intelligence records;
- preserve Product Registry authority for canonical product identity;
- preserve Market Intelligence as a provider-neutral read boundary;
- keep saved research query definitions separate from warehouse observation storage;
- keep warehouse reads evidence-backed and provenance-visible;
- expose persisted records through explicit repository/service boundaries only;
- require a later explicit persistence build before any SQLite schema, migration, or repository is added.

## Candidate future records

A future implementation may define tables or repositories for:

- normalized market observations;
- source/provider provenance;
- offline evidence snapshots;
- saved-query preview history derived from persisted observations;
- import batches and fixture dataset versions.

## Explicit non-goals for this prebuild

Build 700R must not:

- create database tables, migrations, repositories, or SQLite writes;
- persist saved research query definitions or preview results;
- import external files or marketplace data;
- execute live marketplace queries;
- call network providers, scraping services, credentials, cloud sync, alerts, timers, or schedulers;
- add editing, import, delete, run, refresh, or automation controls;
- mutate inventory, listings, pricing, product registry, collection, or any business-domain record;
- infer valuation authority from stored or previewed evidence.

## Future implementation gate

The first persistence implementation must verify:

- schema ownership is explicit and migration-backed;
- records are source-attributed and timestamped;
- product identity references Product Registry authority;
- saved query definitions remain separate from observation storage;
- persisted preview/history reads remain read-only;
- no live provider, network, scheduler, automation, or business-domain mutation authority is introduced.

## Visual verification

Not required for Build 700R because this build is documentation/test-only.

A future implementation that changes Market Intelligence UI or user-visible warehouse behavior will require visual verification.
