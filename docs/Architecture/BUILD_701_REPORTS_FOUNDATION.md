# Build 701 — Reports Foundation Architecture

**Status:** PLANNING — architecture lock only  
**Workstream:** Reports  
**Capability:** CAP-012  
**Foundation issue:** #242  
**Repository authority:** current `main` and existing domain services

## Decision

Build 701 extends MarketDEX with a read-only Reports capability. It must not create a second authority for Inventory, Product Registry, Collection, Pricing, Listing, Settlement, Market Intelligence, or audit history.

Build 701A is documentation-only. No report service, repository, persistence, export, or user interface is authorized by this build.

## Current classification

CAP-012 remains Missing at the canonical operator-workflow level. Current domain services and repositories contain facts that a future Reports capability may query, but those facts remain owned by their existing domains.

Existing calculations, projections, and audit records are source evidence. They are not permission to copy formulas, persist duplicate totals, or introduce a parallel reporting database.

## Ownership boundaries

### Source domains own facts

- Product Registry owns canonical product identity.
- Inventory owns quantities, costs, locations, and inventory lifecycle state.
- Collection owns approved collector-position facts within its separately authorized boundary.
- Pricing owns profit and price-guidance calculations.
- Listing owns listing plans, publication state, and sale workflow evidence.
- Settlement owns settlement evidence, linkage, allocation, verification, and lock authority.
- Market Intelligence owns normalized source observations and evidence-linked derived signals.
- Audit history owns immutable event evidence.

Reports may read approved projections from these domains. Reports must not mutate, reinterpret, or become the authority for their records.

### Reports owns presentation models

Within later explicitly approved slices, Reports may own:

- report definitions;
- deterministic filter and grouping contracts;
- read-only report rows and totals derived from approved source queries;
- provenance describing which source projection produced each value;
- offline export formatting.

Reports does not own source-domain writes, business lifecycle commands, canonical identity, market truth, settlement completion, or accounting authority.

## Dependency direction

Future report presentation must depend on a composition-owned report query service. Presentation code must not open SQLite connections, call repositories directly, or reproduce business formulas.

```text
Approved domain query contracts
        |
        v
Composition-owned report query service
        |
        v
Immutable report read model
        |
        v
Reports workspace or offline export
```

## Offline-first and deterministic behavior

A future report must remain useful without network access. For the same local source state and report parameters, row ordering, grouping, totals, labels, and export output must be deterministic.

Missing or unavailable source data must be shown explicitly. A report must not invent placeholder prices, infer unsupported collection attributes, or present incomplete settlement evidence as complete.

## Provenance and reconciliation rules

Every future report value must identify its source domain or query contract. Cross-domain totals require explicit reconciliation rules and focused tests before implementation.

Reports must distinguish:

- recorded facts from derived values;
- current state from immutable historical evidence;
- inventory reservation from settlement allocation;
- offline fixture evidence from authoritative business records;
- unavailable data from zero values.

## First runtime authorization gate

After Build 701A merges, the smallest permitted implementation candidate is a composition-owned, persistence-free Reports catalog and immutable report-definition contract.

That later slice must remain offline, deterministic, read-only, and UI-free. It must not query live providers, create exports, add database tables, or calculate business totals until separately authorized.

## Verification strategy

Permanent verification for this architecture lock must assert:

- CAP-012 and Build 701 are named explicitly;
- source-domain authority remains unchanged;
- report presentation depends on a composition-owned query boundary;
- offline and deterministic behavior is required;
- persistence, exports, UI, network activity, and mutation remain unauthorized;
- the first later runtime slice is narrow and persistence-free.

## Non-goals for Build 701A

Build 701A does not introduce:

- report services, catalogs, definitions, repositories, or runtime models;
- report workspaces, navigation, charts, dashboards, PDF files, spreadsheets, CSV files, or other exports;
- schema changes, migrations, tables, caches, or duplicate reporting storage;
- writes, imports, background jobs, schedulers, alerts, or automation;
- live providers, network calls, scraping, credentials, or cloud sync;
- changes to business-domain calculations, ownership, or mutation authority.
