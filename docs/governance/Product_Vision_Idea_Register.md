# MarketDEX Product Vision and Idea Register

**Status:** Living approved product-direction authority  
**Owner:** Product Owner  
**Current delivery target:** Windows desktop  
**Future compatibility:** iOS, Android, and web browsers — architecture compatibility only, not current implementation

## Purpose

This document preserves the approved MarketDEX vision, recommendations, product ideas, experience rules, and future possibilities so the project never needs to restart from chat memory.

It consolidates available repository history, foundation documents, recent architecture discussions, and Product Owner approvals. When an older idea conflicts with a newer explicit decision, the newer decision controls and the conflict must be recorded rather than silently ignored.

## Permanent product north star

> **Enter once. Understand everywhere.**

> **Decisions first. Evidence second. Raw metrics on demand.**

MarketDEX should become the best desktop operating system for effortless collectible selling, collection intelligence, market awareness, and safe AI-assisted operation.

The user should understand within approximately sixty seconds:

- what changed
- what deserves attention
- why it matters
- how fresh and trustworthy the evidence is
- what action is safest to consider next

## Approved operating principles

- Offline-first and locally authoritative.
- Desktop-first and optimized for Windows productivity now.
- Future-compatible with iOS, Android, and browsers without building those clients now.
- One permanent codebase and one canonical runtime path.
- Modular business responsibilities instead of disconnected tools.
- Human comprehension before feature count.
- Progressive disclosure: summary first, evidence second, detailed records on demand.
- Charts explain, tables prove, and history remembers.
- Unknown is not zero.
- An estimate is not verified evidence.
- A recommendation is not the user's decision.
- External services may strengthen MarketDEX but must not own its memory.
- AI assistance must follow the same commands, evidence, validation, permissions, and audit rules as human operation.

## Current product scope

### First optimized workflow

Pokémon TCG is the current real-world proving ground and receives the first complete selling and collecting experience.

The desktop app should make it effortless to:

- add or import singles, sealed products, slabs, lots, and supplies
- preserve product identity and set knowledge
- track quantity, cost basis, condition, location, age, and ownership intent
- research raw, graded, sealed, and break/open opportunities
- prepare eBay and TCGplayer listings
- calculate fees, shipping, packaging, and realistic net proceeds
- complete sales, orders, fulfillment, shipping, settlement, and profit history
- decide whether to keep, watch, sell, trade, grade, open, break, or keep sealed
- understand portfolio and collection movement
- identify what needs attention without studying every metric

### Approved category extensibility

Shared architecture must support explicit category extensions for:

- other trading card games
- sealed gaming products
- graded collectibles
- Funko Pops
- gaming collectibles
- related collectible products

Category expansion must not weaken the Pokémon workflow or create duplicate applications.

## Platform direction

### Current

- Windows desktop app
- PySide6 presentation
- SQLite offline-first persistence
- Windows executable and installer
- keyboard, mouse, large-screen, accessibility, and productivity optimization

### Future only

- iOS client
- Android client
- browser client
- optional multi-device synchronization
- optional shared or hosted services

Future clients should reuse domain rules, commands, queries, read models, and provider contracts. No mobile or web application tree should be created during the desktop-first phase.

## Approved architecture foundation

MarketDEX should use the following separation:

```text
Desktop Presentation
        ↓
Application Commands, Queries, Workflows, and Read Models
        ↓
Domain Entities, Value Objects, Policies, and Decision Rules
        ↓
Repository, Marketplace, Trend, File, and AI Provider Interfaces
        ↓
SQLite, CSV, APIs, Windows Files, and Other Replaceable Adapters
```

### Mandatory architectural capabilities

- one launcher and one shell
- one application composition root
- one workspace registry
- one feature/module catalog with explicit dependencies
- one persistence, schema, and migration authority
- stable identities independent from widget indexes
- typed commands, queries, events, and transfer contracts
- view models/controllers between widgets and application services
- repository and provider protocols
- deterministic calculations separated from UI
- structured audit history
- transactional migrations with backup and rollback
- background jobs with progress, cancellation, retry, and history
- diagnostics, structured logs, version manifest, and support export
- architecture enforcement through CI and repository checkpoints

## Approved domain modules

The permanent modular model should accommodate:

1. **Catalog** — canonical collectible product identity, variants, editions, sets, forms, and category extensions.
2. **Inventory** — business-owned positions, quantity, cost layers, location, age, state, lineage, and readiness.
3. **Collection** — personally held positions, goals, favorites, never-sell intent, completion, trade/sell willingness, and collector decisions.
4. **Purchasing** — sources, acquisition evidence, receiving, lots, taxes, and purchase outcomes.
5. **Pricing** — pricing policies, fees, shipping, packaging, target margins, and net-proceeds decisions.
6. **Market Data** — source observations, sold/listed prices, supply, volume, population, attention, sentiment, freshness, and confidence.
7. **Listings** — preparation, content, photos, condition, price decision, marketplace readiness, publication evidence, and listing history.
8. **Orders and Fulfillment** — order obligations, packing, shipping, delivery, exceptions, and operational burden.
9. **Sales and Settlement** — sale agreement, fees, payouts, settlement evidence, deductions, net profit, and capital state.
10. **Portfolio** — analytical views across inventory and collection without becoming a second ownership authority.
11. **Attention** — explainable ranking of risks, opportunities, stale evidence, blockers, and actions.
12. **Research** — watchlists, hypotheses, experiments, comparisons, source evidence, and decision history.
13. **Reports and Insights** — historical read models, exports, trends, taxes-ready evidence boundaries, and performance analysis.
14. **Settings and Policies** — user preferences, business assumptions, thresholds, storage, marketplace rules, secrets, and runtime state.
15. **Jobs and Notifications** — long-running work, progress, failures, retries, completion, and user-visible delivery.
16. **Integrations** — marketplace, pricing, grading, trends, import, export, and future connector adapters.
17. **AI Assistance** — safe read models, controlled tools/commands, explanations, evidence links, and audit.

## Approved user-facing workspaces

- **Mission Control** — what deserves attention now
- **Inventory** — business-owned items and selling readiness
- **Collection** — personally held items and collector goals
- **Pricing** — selected-item economics and pricing decisions
- **Listings** — preparation through listing execution
- **Orders & Shipping** — fulfillment and exceptions
- **Sales & Settlement** — outcomes, payouts, and true profit
- **Market Compass** — marketplace comparison, spreads, liquidity, and net proceeds
- **Collector Pulse** — watchlists, movement, volume, sentiment, scarcity, and attention
- **Research Lab** — deep evidence, hypotheses, grading, products, and experiments
- **Portfolio** — value, allocation, concentration, and performance
- **Reports & Insights** — detailed historical analysis and exports
- **Settings** — preferences, policies, integrations, backups, diagnostics, and maintenance

Workspaces may be introduced gradually. The shell must not know their internal implementation details.

## Business Mode and Collector Mode

Modes are presentation and prioritization lenses over shared authoritative data. They are not separate databases or duplicate applications.

### Business Mode emphasis

- profit and ROI
- cash and capital tied up
- inventory age and turnover
- listing readiness
- sell-through
- fees, shipping, and packaging
- best marketplace by realistic net proceeds
- order and settlement attention
- products to list, reprice, sell, or redeploy

### Collector Mode emphasis

- collection value and movement
- set and goal completion
- allocation and concentration
- scarcity and population
- grading potential
- favorites and never-sell intent
- watchlists and market attention
- keep, watch, trade, sell, open, or keep sealed analysis

The app should remember the last-used mode while allowing an obvious toggle.

## Mission Control visual hierarchy

Mission Control remains the default decision surface and should stay simple:

1. **Today's Top 3 / Needs Attention**
2. **Capital Health**
3. **Opportunity + Risk**
4. **Business Scoreboard**
5. **Visual Intelligence**

Default visuals should be limited to the most useful summary:

- value or capital trend line chart
- marketplace net-proceeds bar comparison
- allocation pie/donut chart
- ranked Needs Attention queue
- freshness and confidence indicators

Detailed heat maps, volume, sentiment, Google Trends, evidence tables, and additional metrics should appear through expansion or dedicated workspaces.

## Approved visual intelligence

Reusable visualization components should support:

- line charts for change over time
- bar charts for comparison and ranking
- stacked bars for composition over time
- pie/donut charts only for understandable part-to-whole relationships
- sparklines for compact movement
- heat maps for attention, opportunity, concentration, and movement clusters
- daily sold-volume indicators
- supply and listing-count movement
- market sentiment composites
- confidence and freshness badges
- 7-day, 30-day, 90-day, 1-year, and all-history ranges

Every chart must have a metric owner, a business question, a freshness state, and a drill-down evidence path.

## Market intelligence and marketplace ideas

### Initial sources and marketplaces

- eBay
- TCGplayer
- Collectr
- PSA population/reference evidence
- manual/local sales
- CSV imports
- future authorized marketplaces and providers

### Observation families

- active listing
- confirmed sold transaction
- market/reference price
- shipping cost
- marketplace fee
- estimated net proceeds
- observable supply
- daily sales volume
- graded population
- retail availability/restock/reprint
- Google Trends relative search interest
- source confidence and freshness

### Permanent market rules

- Normalize observations through replaceable adapters.
- Store raw source evidence separately from standardized values and derived intelligence.
- Preserve source, observed time, imported time, geography, query, sample size, confidence, and freshness.
- Prefer realistic net proceeds and liquidity over the highest visible asking price.
- Google Trends is relative 0–100 attention evidence, not absolute demand or proof of future price.
- Price movement should be interpreted with volume, supply, duration, population, source agreement, and context.
- External adapters may submit observations but may not mutate canonical business authority directly.

## Attention and pattern-recognition ideas

The hidden Attention Engine should rank explainable candidates across modules rather than letting every module claim urgency.

Potential signals include:

- price change beyond policy threshold
- marketplace divergence
- net proceeds below target margin
- strong sales volume with falling supply
- price increase unsupported by volume
- stale or missing market evidence
- underpriced or aging listings
- low inventory or excess concentration
- capital trapped too long
- grading opportunity requiring review
- keep-sealed/open value disconnect
- unusual Google Trends attention
- upcoming release, holiday, convention, or seasonal window
- order, shipping, settlement, or reconciliation exception
- product needing only one preparation step before listing

Every signal should expose severity, confidence, freshness, explanation, evidence, suggested action, and dismiss/snooze behavior.

## Keep, sell, grade, open, and sealed analysis

MarketDEX should compare evidence-supported paths without pretending to predict guaranteed outcomes:

- KEEP
- WATCH
- CONSIDER SELLING
- TRADE
- LIST
- REPRICE
- GRADE
- OPEN
- BREAK
- KEEP SEALED
- WAIT
- REDEPLOY CAPITAL

### Sealed-versus-open analysis

The dedicated decision section should support:

- sealed market value
- acquisition cost
- packs per product
- price per pack
- expected contents/reference value
- transaction and selling costs
- uncertainty and data freshness
- liquidity and operational burden
- collection intent
- sealed scarcity and replacement difficulty

The recommendation must remain explainable and user-controlled.

## Complete selling workflow

The preferred operational chain is:

```text
Purchase → Receive → Catalog Match → Inventory/Collection Decision
→ Research → Listing Preparation → Price Decision → Marketplace Choice
→ List → Sell → Order → Pack → Ship → Deliver/Resolve Exception
→ Settlement → True Net Outcome → Capital State → Learn
```

The user should not re-enter facts already captured by an authoritative earlier event.

## Historical intelligence and learning

MarketDEX should distinguish:

- current state
- immutable or append-only event history
- meaningful snapshots
- decisions and assumptions
- experiments
- outcomes
- source and connector history
- rule/model version used for a recommendation

History should support reaction-lag studies, seasonal windows, release behavior, marketplace performance, product/category performance, grading outcomes, shipping outcomes, decision quality, and capital recycling.

## AI-assisted operation

People and authorized AI assistants should use the same controlled application contracts.

AI may:

- search and summarize approved read models
- explain calculations and attention signals
- prepare drafts, listing content, comparisons, and research notes
- propose commands and workflows
- surface missing evidence and contradictions

AI may not:

- write directly to SQLite
- bypass validation or authority rules
- invent verified prices, sales, costs, or identities
- publish listings, spend money, delete data, or perform destructive actions without explicit authority
- present uncertain recommendations as guarantees

AI outputs should preserve evidence references, freshness, confidence, calculation/rule version, and an audit record when consequential.

## Upgradability, reliability, and operations

Approved future capabilities include:

- automatic pre-migration backups
- transactional schema upgrades
- rollback and recovery plans
- historical database upgrade fixtures
- migration history and checksums
- import previews and validation
- duplicate detection and identity reconciliation
- scheduled local jobs
- job progress, cancellation, retry, and history
- automatic backup health checks
- exportable diagnostics bundle
- structured logs with sensitive-data protection
- version and capability manifest
- settings separation for preferences, business policies, secrets, and runtime state
- official adapters first; manual/CSV fallback always preserved where practical

## Accessibility and ease-of-use

- Use plain language and consistent names.
- Avoid red/green-only meaning; pair color with text and symbols.
- Preserve keyboard navigation and useful shortcuts.
- Keep primary actions visible and destructive actions guarded.
- Make freshness and confidence understandable.
- Use saved filters/views without hiding authoritative data.
- Avoid walls of metrics.
- Keep advanced analysis available without making it the default.
- Explain why a recommendation exists and what evidence would change it.

## Future possibilities preserved, not current commitments

- mobile and browser clients
- optional synchronization
- barcode or image-assisted identification
- camera-assisted condition and inventory intake
- official marketplace publishing and order connectors
- grading submission workflows
- release calendars and product-drop preparation
- richer seasonality and event-window analysis
- local or hosted AI models
- collaboration and multi-user roles
- plugin/category packs
- gamification for authoritative progress, badges, and major milestones

These ideas require separate approval at implementation time when they introduce paid services, credentials, privacy risk, destructive behavior, or major scope change.

## Explicit current non-goals

- building iOS, Android, or browser UIs now
- creating a second active application shell
- cloud-first storage
- uncontrolled scraping
- direct AI database access
- unexplained automatic buy/sell decisions
- adding charts only for decoration
- duplicating data authority by module or marketplace
- hard-coding the permanent domain exclusively to Pokémon

## Idea capture and continuity rule

Every material new idea must be classified as one of:

- **APPROVED — CURRENT**: part of the active desktop product
- **APPROVED — FOUNDATION**: architecture must support it now
- **APPROVED — FUTURE**: preserve compatibility; do not implement yet
- **RESEARCH**: evidence or product decision still needed
- **REJECTED/SUPERSEDED**: retained with reason so it is not rediscovered

Each material architecture or feature PR must update this register or explicitly state that it introduces no new product idea.

No chat summary alone is product authority. Repository-backed documents, accepted specifications, merged implementation, tests, CI, and checkpoint evidence control.
