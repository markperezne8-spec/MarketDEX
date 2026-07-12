# Build 700K — Research Query Workspace Prebuild

**Status:** PLAN — read-only workspace integration classification  
**Workstream:** Market Intelligence  
**Repository authority:** `MarketIntelligenceComposition`, the in-memory research query catalog, and the existing Market Intelligence workspace

## Decision

Build 700K classifies the next operator-facing slice after the in-memory saved research query contract. It authorizes planning for a read-only presentation of saved research query definitions inside the existing Market Intelligence workspace.

This build is documentation-only. It does not authorize runtime UI changes.

## Existing permanent evidence

- Market Intelligence is mounted through the permanent application composition.
- The workspace is read-only and offline-safe.
- Build 700J introduces a provider-neutral in-memory research query catalog owned by `MarketIntelligenceComposition`.
- Product Registry remains the authority for canonical `product_id` identity.

## Proposed read-only presentation

A later implementation may display:

- query identifier;
- operator-facing name;
- canonical product references;
- marketplace filters;
- observation-kind filters;
- optional descriptive notes;
- deterministic catalog order.

The presentation must not expose provider-specific payloads or execution controls.

## Authority boundaries

### Market Intelligence may

- read definitions from the composition-owned catalog;
- display normalized values;
- show an explicit in-memory and non-persistent status;
- remain useful with no network connection.

### Market Intelligence must not

- create, edit, delete, import, or persist definitions;
- execute provider calls;
- schedule background work;
- create alerts or automated actions;
- mutate Product Registry, Inventory, Collection, Listing, Portfolio, Reports, or Settlement.

## Empty and unavailable states

The later workspace slice must distinguish:

- no saved research queries registered;
- catalog available with definitions;
- invalid definition rejected before registration;
- runtime provider data unavailable without affecting definition visibility.

## Verification strategy

A later implementation must verify:

- the existing workspace remains mounted once;
- the query table is read-only;
- row ordering matches catalog ordering;
- canonical product references are rendered without creating aliases;
- no database file, migration, provider call, timer, or mutation is introduced;
- existing Market Intelligence evidence and visualization remain intact.

## Build 700L implementation gate

The next authorized runtime slice after this prebuild is a read-only saved research query table in the existing Market Intelligence workspace.

Build 700L may:

- add one read-only table or section;
- consume only the composition-owned in-memory catalog;
- show explicit in-memory/offline status;
- add focused UI contract tests.

Build 700L must not:

- add editing controls;
- add persistence or migrations;
- call live providers;
- add alerts, schedulers, or automated execution;
- alter existing domain authority.

## Visual verification

Not required for Build 700K because this build is documentation-only.
