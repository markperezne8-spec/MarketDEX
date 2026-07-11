# MarketDEX Approved Architecture Roadmap

## Approval authority

On 2026-07-11, the Product Owner approved the available MarketDEX architecture and product recommendations from the modernization discussions and repository history, except where a newer explicit decision or established source-of-truth rule supersedes an older idea.

Approval authorizes controlled planning, implementation, validation, and ordered progression through the architecture work. It does not authorize destructive data changes, paid services, credential use, publishing, spending, or merging pull requests before applicable gates are green and final heads are verified.

## Permanent continuity authorities

- `docs/governance/Product_Vision_Idea_Register.md` — living approved idea and product-direction register
- `docs/governance/Canonical_Product_Terminology.md` — user-facing naming and compatibility authority
- `docs/Architecture/Modular_Collectibles_Platform_Blueprint.md` — target modular architecture
- `docs/governance/Platform_Strategy.md` — desktop-first and future-client boundaries
- `docs/governance/Architecture_Gates.md` — mandatory pass/fail framework
- `FoundationCheckpoint.md` — current state and exact resume point
- latest EC checkpoint — detailed in-progress evidence

Every material new idea must be preserved in the idea register or explicitly classified as a duplicate, rejected, or superseded concept.

## Product direction

- Build the best desktop operating system for effortless collectible selling and collection intelligence.
- Optimize the first complete experience for Pokémon TCG.
- Keep the permanent model extensible to other TCGs, gaming products, Funko Pops, graded items, and related collectibles.
- Remain offline-first and subscription-free where comparable value is practical.
- Present decisions first, evidence second, and raw metrics on demand.
- Support safe AI-assisted workflows through the same commands, authority rules, evidence, and audit trail used by people.
- Preserve future iOS, Android, and web compatibility without building those clients now.
- Preserve simple, canonical user-facing names while allowing controlled compatibility aliases for existing IDs.

## Approved foundation sequence

1. Canonical product vision and idea continuity.
2. Canonical product terminology and compatibility mappings.
3. Canonical shell and workspace authority.
4. Canonical application composition root.
5. Dependency-safe feature and module catalogs.
6. One persistence, schema, and migration authority.
7. Reconcile or retire competing legacy application trees.
8. Dedicated Catalog, Inventory, Collection, Pricing, Listings, Orders, Sales, Market Data, Attention, Portfolio, Reporting, Research, Settings, Jobs, Integrations, and AI modules.
9. View models and controllers between widgets and application services.
10. Typed command, query, event, and data-transfer architecture.
11. Repository and provider interfaces with in-memory test implementations.
12. Durable settings, business-policy, secret, and runtime-state separation.
13. Transactional schema upgrades, backups, rollback, and historical database fixtures.
14. Background jobs with progress, cancellation, retry, error reporting, and history.
15. Replaceable marketplace, import, export, pricing, grading, and trend adapters.
16. Canonical market-observation history and cross-marketplace comparison read models.
17. Explainable attention, keep/sell, reprice, grade, open/keep-sealed, and marketplace-opportunity signals.
18. Mission Control, Collection, Market Compass, Collector Pulse, Research Lab, Portfolio, Reports & Insights, and other dedicated workspaces.
19. Reusable line, bar, stacked-bar, pie/donut, heat-map, daily-volume, sentiment, and sparkline components.
20. Task Center, notifications, diagnostics bundle, structured logging, version manifest, and support tooling.
21. Controlled AI tools backed by stable read models and commands.
22. Architecture enforcement in CI and mandatory repository checkpoints.

## Approved experience direction

### Business Mode

Focus on profit, ROI, cash tied up, inventory age, sell-through, listing readiness, fees, shipping, settlement, and marketplace net proceeds.

### Collector Mode

Focus on collection value, watchlists, allocation, set completion, scarcity, grading potential, market movement, and sealed-product decisions.

Modes are presentation lenses over the same authoritative products, ownership, observations, and evidence. They are not separate databases or applications. The desktop app should remember the last-used mode and provide a clear toggle.

### Default overview

The default view should remain simple:

- ranked Needs Attention queue
- collection, inventory, or capital value trend
- marketplace net-proceeds comparison
- allocation composition
- freshness and confidence indicators

Heat maps, volume, sentiment, Google Trends, detailed evidence, and additional metrics remain available through expansion or dedicated workspaces.

## Approved user-facing names

- Mission Control
- Inventory
- Collection
- Pricing
- Listings
- Orders & Shipping
- Sales & Settlement
- Market Compass
- Collector Pulse
- Research Lab
- Portfolio
- Reports & Insights
- Settings

`Canonical_Product_Terminology.md` controls conflicts and legacy aliases. Existing persisted IDs are not renamed without compatibility migration and regression evidence.

## Approved market-intelligence direction

- Normalize eBay, TCGplayer, Collectr, PSA, local/manual activity, and future sources through replaceable adapters.
- Treat Google Trends as normalized relative search interest, never as absolute demand proof.
- Prefer net proceeds and liquidity over the highest visible listing price.
- Store source, observed time, import time, confidence, freshness, sample size, geography/query where relevant, and evidence identity.
- Preserve raw observations separately from standardized metrics and derived intelligence.
- Never allow external adapters to write directly to canonical business-authority tables.
- Never issue unexplained Buy, Sell, Keep, Grade, Open, or Keep Sealed recommendations.

## Approved AI direction

- AI uses approved queries/read models and commands.
- AI never mutates SQLite directly.
- Deterministic business calculations remain normal code, not probabilistic AI output.
- Consequential AI proposals preserve evidence, freshness, confidence, permission, validation, and audit.
- Publishing, spending, destructive changes, and sensitive external actions require explicit authority.

## Approved implementation bundles

### Bundle A — Foundation authority

- shell and workspace authority
- composition root
- feature/module dependency validation
- naming and idea continuity
- architecture gates

### Bundle B — Data and upgradability

- persistence reconciliation
- schema/migration authority
- backups and rollback
- historical upgrade fixtures
- identity and audit conventions

### Bundle C — Modular application contracts

- module definitions
- commands, queries, events, and read models
- repositories/providers
- view models/controllers
- selection/context events

### Bundle D — Decision-focused desktop experience

- Business/Collector toggle
- Mission Control and Collection overview
- canonical charts
- Needs Attention
- marketplace comparison
- sealed/open and grading decisions

### Bundle E — Operations and integrations

- imports and exports
- jobs and notifications
- marketplace/trend adapters
- orders, shipping, settlement, and diagnostics

### Bundle F — Safe AI and future extension

- AI tool contracts
- category extension packs
- future-client-compatible DTOs and APIs
- optional future synchronization only after desktop excellence

## Execution rule

Work proceeds in small, reviewable, gated changes. Each material change must preserve the current working application, declare idea and naming impact, add focused tests, pass applicable CI and packaging gates, and update repository-backed checkpoint evidence.