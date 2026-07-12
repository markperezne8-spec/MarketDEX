# Build 700I — Saved Research Query Definitions Prebuild Classification

**Status:** PLAN — documentation-only authority classification  
**Workstream:** Market Intelligence  
**Issue:** #201  
**Repository authority:** `main` in `markperezne8-spec/MarketDEX`

## Decision

Build 700I defines the minimum provider-neutral contract for read-only saved research query definitions. This build does not authorize runtime persistence, provider execution, background jobs, alerts, or mutation of any canonical business domain.

## Permitted definition vocabulary

A future query definition may contain only:

- `query_id`: stable internal identifier;
- `name`: operator-facing label;
- `product_id`: optional canonical Product Registry identity reference;
- `marketplace_id`: optional marketplace catalog reference;
- `observation_kinds`: one or more existing normalized observation kinds;
- `mode_id`: optional Market Intelligence presentation-mode reference;
- `created_at`: explicit UTC creation time;
- `rule_version`: deterministic contract version;
- `notes`: optional operator-authored text.

The contract must remain provider-neutral. It must not embed credentials, provider payloads, network URLs, scraping instructions, executable expressions, mutation commands, or automated action settings.

## Authority boundaries

- Product Registry remains the sole owner of canonical product identity.
- Market Intelligence may own the definition of a research query only after a later persistence build is separately approved.
- Observation providers remain replaceable adapters behind the normalized observation gateway.
- Query definitions may request evidence but may not create, alter, or delete Inventory, Collection, Listing, Portfolio, Reports, or Settlement facts.
- Recommendations and signals remain advisory and read-only.

## Offline-first rule

Definitions must be inspectable and valid without network access. A provider being unavailable must not invalidate the definition itself. Execution results, provider availability, and observations are separate concerns.

## Validation requirements

A later runtime contract must fail closed for:

- blank identifiers or names;
- unknown observation kinds;
- duplicate observation kinds;
- non-UTC timestamps;
- provider-specific fields;
- executable or mutation-bearing content;
- unknown catalog references when validation context is available.

Ordering and serialization must be deterministic.

## Persistence gate

Build 700I does not authorize database tables, migrations, repositories, CRUD commands, archive semantics, or synchronization. Any persistence proposal requires a separate build that defines ownership, uniqueness, lifecycle, migration, and restart-reconstruction guarantees.

## Selected next implementation gate

A later Build 700J may introduce an immutable in-memory `ResearchQueryDefinition` value object and deterministic validation tests only. It must not add persistence, UI, live providers, background execution, alerts, or automated actions.

## Verification strategy

Permanent tests for a future runtime slice must cover:

- provider-neutral fields only;
- canonical identity references;
- deterministic normalization and ordering;
- fail-closed invalid inputs;
- explicit UTC handling;
- zero mutation of canonical business domains;
- no network or provider-specific dependencies.

## Visual verification

Not required. This build is documentation-only.
