# Build 700U — Market Intelligence Warehouse Repository Boundary Prebuild

## Purpose

Build 700U defines the repository boundary for a future offline Market Intelligence warehouse without implementing repository interfaces, persistence, migrations, or database writes.

The future repository layer must remain provider-neutral, offline-first, provenance-visible, and separate from business-domain mutation authority.

## Read and write separation

A future implementation must separate read responsibilities from write responsibilities.

### Future write boundary

A future write repository may eventually support:

- append-only ingestion of normalized warehouse observations;
- registration of immutable source and provenance records;
- creation of immutable snapshots and snapshot membership;
- recording of saved-query preview history derived from persisted observations.

Future writes must:

- use explicit transaction boundaries;
- be idempotent for repeated import or ingestion attempts;
- reject conflicting duplicate identifiers;
- preserve original observation timestamps and source attribution;
- reference canonical Product Registry product IDs without becoming product identity authority;
- avoid updates that rewrite historical observation facts in place.

### Future read boundary

A future read repository may eventually support:

- retrieving observations by canonical product ID, source, kind, and time range;
- retrieving source and provenance details;
- retrieving immutable snapshots and snapshot membership;
- retrieving read-only saved-query preview history;
- deterministic ordering for all returned records.

Future reads must remain read-only and must not execute live provider queries, infer valuation authority, or mutate any business-domain record.

## Authority rules

The future warehouse repository layer must:

- preserve Product Registry authority for canonical product identity;
- preserve Market Intelligence as the provider-neutral read boundary;
- keep saved research query definitions separate from observation storage;
- keep source attribution and provenance visible;
- expose repository behavior through explicit application services;
- avoid direct UI ownership of repository or transaction authority.

## Explicit non-goals for this prebuild

Build 700U must not:

- add repository protocols, interfaces, implementations, or adapters;
- create SQLite schema, migrations, tables, connections, or writes;
- import files, seed records, or persist fixtures;
- call live providers, networks, scraping services, credentials, alerts, schedulers, or cloud sync;
- add UI controls or user-visible behavior;
- mutate inventory, listings, pricing, Product Registry, collection, or any other business-domain record.

## Future implementation gate

Before repository code is introduced, a later explicit build must verify:

- the Build 700T immutable domain models are stable;
- schema and migration ownership is explicit;
- read and write contracts are separated;
- write operations are transaction-scoped and idempotent;
- observation history is append-only;
- timestamps, source attribution, provenance, and canonical product references are preserved;
- no live-provider, automation, valuation, or business-domain mutation authority is introduced.

## Visual verification

Not required for Build 700U because this build is documentation/test-only.