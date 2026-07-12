# Build 700 — Market Intelligence Foundation

**Status:** PARTIAL — offline read-only operator slice delivered  
**Workstream:** Market Intelligence  
**Foundation issue:** #183  
**Status reconciliation issue:** #199  
**Repository authority:** existing `market_intelligence` package and permanent application composition

## Decision

Build 700 extends the existing Market Intelligence foundation. It must not create a second composition root, provider registry, observation model, recommendation model, or visualization catalog.

The current implementation is classified as a **delivered Partial capability**. It now provides a provider-neutral fixture-backed observation gateway, deterministic attention-signal derivation, an application-owned read-only workspace, an offline Market Signal Explorer, and a catalog-backed offline sample evidence visualization.

No live provider is approved. No persistent market-price authority is approved. No automated execution authority is approved.

## Delivered Build 700 evidence

- Build 700A / PR #184 locked the architecture and authority boundaries.
- Build 700B / PR #186 added the provider-neutral, fixture-backed Market Observation Gateway.
- Build 700C / PR #188 added the deterministic Market Attention Signal service.
- Build 700D / PR #192 mounted the read-only Market Intelligence workspace in the desktop shell.
- Build 700E / PR #194 added the offline Market Signal Explorer using normalized fixture evidence.
- Build 700F / PR #196 added the first catalog-backed offline sample evidence visualization for observed price and daily volume.

The delivered operator slice remains offline-first, read-only, deterministic, source-attributed, and non-authoritative for valuation or execution.

## Existing permanent evidence

- `market_intelligence/composition.py` owns the mode, marketplace, visualization, observation-gateway, and attention-signal composition.
- `composition/application_composition.py` owns one `MarketIntelligenceComposition` instance.
- `market_intelligence/modes.py` separates Business and Collector presentation categories.
- `market_intelligence/marketplaces.py` declares provider capabilities without performing network access.
- `market_intelligence/observations.py` models source-attributed market observations.
- `market_intelligence/observation_gateway.py` provides the provider-neutral gateway boundary.
- `market_intelligence/offline_fixtures.py` provides deterministic offline fixture evidence.
- `market_intelligence/trends.py` models ordered relative-interest series.
- `market_intelligence/attention.py` models evidence-backed attention signals and suggested review actions.
- `market_intelligence/attention_service.py` derives deterministic read-only attention signals.
- `market_intelligence/sealed_decision.py` provides a pure sealed-versus-open decision calculation.
- `market_intelligence/visualizations.py` declares supported visualization contracts.
- `ui/market_intelligence_workspace.py` presents readiness, evidence, signals, and relative offline evidence bars.
- `tests/test_market_intelligence_foundation.py` verifies composition ownership and domain contracts.
- `tests/test_build700b_market_observation_gateway.py` verifies gateway behavior and provider isolation.
- `tests/test_build700c_market_attention_signals.py` verifies deterministic signal derivation and evidence preservation.
- `tests/test_build700d_market_intelligence_workspace.py` verifies the read-only workspace, explorer, and visualization surface.

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

Within separately approved slices, Market Intelligence may own:

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
- observation rejected or low-confidence;
- deterministic fixture evidence used for offline verification.

No placeholder price, fake trend, or inferred market fact may be shown as authoritative data. Fixture-backed values must remain visibly labeled as offline sample evidence.

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

## Delivered partial boundary

Builds 700B through 700F prove a safe read-only vertical slice. They do not authorize:

- live external-provider calls;
- credentials or secrets storage;
- scraping or browser automation;
- persistent market-price or valuation authority;
- background refresh jobs;
- automatic alerts that execute actions;
- automatic buying, selling, grading, restocking, repricing, or listing;
- mutation of Product Registry, Inventory, Collection, Listing, Portfolio, Reports, or Settlement.

## Verification strategy

Permanent verification must cover:

- one application-owned Market Intelligence composition;
- stable provider identifiers and capability declarations;
- source and confidence preservation;
- deterministic calculations and ordering;
- fail-closed invalid inputs;
- explicit offline/unavailable behavior;
- fixture evidence labeling;
- zero mutation of canonical business domains;
- no provider-specific dependencies in presentation code;
- repository status documentation that cites delivered PR evidence without expanding authority.

## Next authorization gate

Further runtime work requires a new repository-backed issue that explicitly selects one narrow extension. A future build must not infer approval for live providers, persistence, background jobs, alerts, valuation authority, or execution commands from the delivered offline read-only slice.

## Non-goals

- live provider integrations;
- cloud synchronization;
- speculative price or valuation persistence;
- automated buying, selling, grading, restocking, or listing;
- AI-generated recommendations without evidence contracts;
- Portfolio or Reports implementation;
- replacement of existing `market_intelligence` modules.
