# Build 700 — Market Intelligence Foundation

**Status:** PLAN — architecture reconciliation and authority lock  
**Workstream:** Market Intelligence  
**Issue:** #183  
**Repository authority:** existing `market_intelligence` package and permanent application composition

## Decision

Build 700 extends the existing Market Intelligence foundation. It must not create a second composition root, provider registry, observation model, recommendation model, or visualization catalog.

The current implementation is classified as a **Partial foundation**. It already provides stable application-owned catalogs and pure domain models, but it does not yet provide approved live-provider ingestion, persistent observation authority, or an operator workspace.

## Existing permanent evidence

- `market_intelligence/composition.py` owns the mode, marketplace, and visualization catalogs.
- `composition/application_composition.py` owns one `MarketIntelligenceComposition` instance.
- `market_intelligence/modes.py` separates Business and Collector presentation categories.
- `market_intelligence/marketplaces.py` declares provider capabilities without performing network access.
- `market_intelligence/observations.py` models source-attributed market observations.
- `market_intelligence/trends.py` models ordered relative-interest series.
- `market_intelligence/attention.py` models evidence-backed attention signals and suggested review actions.
- `market_intelligence/sealed_decision.py` provides a pure sealed-versus-open decision calculation.
- `market_intelligence/visualizations.py` declares supported visualization contracts.
- `tests/test_market_intelligence_foundation.py` verifies composition ownership and the current domain contracts.

## Authority boundaries

### Product Registry owns identity

Market Intelligence references canonical `product_id`. It must not create substitute product identities, aliases, set identities, or card-number authority.

### Inventory owns business positions

Market Intelligence may read inventory quantities, costs, and listing context through approved query contracts. It must not change quantity, cost basis, reservation, publication, or sale state.

### Collection owns collector positions

Market Intelligence may eventually read approved Collection facts. It must not create collector intent, condition, grade, provenance, or ownership transitions.

### Listing and Settlement own execution

Recommendations such as review, hold, sell, grade, or restock are advisory. They must never publish a listing, complete a sale, allocate settlement evidence, or alter financial authority.

### Market Intelligence owns derived evidence

Once separately approved, Market Intelligence may own:

- normalized source observations;
- source and confidence metadata;
- deterministic derived metrics;
- evidence-linked attention signals;
- read-only recommendations;
- saved research query definitions.

It does not own external-provider truth. Every observation must preserve its source, observed time, confidence, and supporting evidence.

## Dependency direction

```text
External Provider Adapter
        |
        v
Normalized Observation Contract
        |
        v
Deterministic Derivation / Decision Services
        |
        v
Attention Signals and Read-only Recommendations
        |
        v
Research / Dashboard Presentation
```

No downstream presentation component may bypass the normalized observation boundary and call a provider directly.

## Provider adapter contract

A future provider adapter must:

1. have a stable provider identifier;
2. declare supported capabilities;
3. return normalized, source-attributed observations;
4. preserve observation timestamps and sample information;
5. fail without mutating canonical business domains;
6. support explicit offline and unavailable states;
7. avoid exposing provider-specific payloads beyond the adapter boundary;
8. use credentials only through an approved secrets mechanism;
9. comply with provider terms and rate limits;
10. remain replaceable without changing Product Registry, Inventory, Collection, or presentation contracts.

## Offline-first rule

The desktop application must start and remain useful without network access. Provider unavailability must not block Inventory, Collection, Product Registry, Listing, Settlement, or the desktop shell.

Market Intelligence presentation must distinguish:

- no observation recorded;
- cached observation available;
- provider unavailable;
- observation stale;
- observation rejected or low-confidence.

No placeholder price, fake trend, or inferred market fact may be shown as authoritative data.

## Recommendation rule

A recommendation must include:

- subject identity;
- recommendation or suggested action;
- human-readable explanation;
- confidence;
- evidence identifiers;
- creation time;
- deterministic rule or model version when applicable.

Recommendations are read-only decision support. User approval and the owning domain command are always required for execution.

## Build 700A deliverable

This architecture lock is documentation-only. It reconciles the existing foundation and prevents duplicate or speculative implementation.

## Build 700B implementation gate

The next authorized implementation slice is a **read-only Market Observation Gateway contract** using an in-memory or fixture-backed adapter. Build 700B may:

- define a provider-neutral adapter protocol;
- define explicit success, unavailable, stale, and rejected result states;
- normalize fixture observations into the existing `MarketObservation` model;
- register adapters through the existing `MarketIntelligenceComposition`;
- add deterministic tests for source preservation, ordering, offline behavior, and zero mutation.

Build 700B must not:

- call a live external API;
- add credentials;
- scrape websites;
- persist market prices;
- create automatic alerts or actions;
- modify Product Registry, Inventory, Collection, Listing, Portfolio, Reports, or Settlement authority.

## Verification strategy

Permanent verification must cover:

- one application-owned Market Intelligence composition;
- stable provider identifiers and capability declarations;
- source and confidence preservation;
- deterministic calculations and ordering;
- fail-closed invalid inputs;
- explicit offline/unavailable behavior;
- zero mutation of canonical business domains;
- no provider-specific dependencies in presentation code.

## Non-goals

- live provider integrations;
- cloud synchronization;
- speculative price or valuation persistence;
- automated buying, selling, grading, restocking, or listing;
- AI-generated recommendations without evidence contracts;
- Portfolio or Reports implementation;
- replacement of existing `market_intelligence` modules.
