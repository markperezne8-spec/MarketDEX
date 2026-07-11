# MarketDEX Approved Architecture Roadmap

## Approval authority

On 2026-07-11, the Product Owner approved the architecture and product recommendations from the recent MarketDEX modernization discussions. This document consolidates that approval into one repository-backed execution backlog.

Approval authorizes controlled implementation, validation, and ordered progression through the stacked architecture work. It does not authorize destructive data changes, paid services, credential use, or merging pull requests before the applicable gates are green and the final stacked heads are verified.

## Product direction

- Build the best desktop operating system for effortless collectible selling and collection intelligence.
- Optimize the first complete experience for Pokémon TCG.
- Keep the permanent model extensible to other TCGs, gaming products, Funko Pops, and related collectibles.
- Remain offline-first and subscription-free where comparable value is practical.
- Present decisions first, evidence second, and raw metrics on demand.
- Support safe AI-assisted workflows through the same commands, authority rules, evidence, and audit trail used by people.
- Preserve future iOS, Android, and web compatibility without building those clients now.

## Approved architecture sequence

1. Canonical shell and workspace authority.
2. Canonical application composition root.
3. Dependency-safe feature and module catalogs.
4. One persistence, schema, and migration authority.
5. Reconcile or retire competing legacy application trees.
6. Dedicated Inventory, Pricing, Listing, Collection, Marketplace, Reporting, and Research modules.
7. View models and controllers between widgets and application services.
8. Typed command and event architecture.
9. Repository and provider interfaces with in-memory test implementations.
10. Durable settings, business-policy, secret, and runtime-state separation.
11. Transactional schema upgrades, backups, rollback, and historical database fixtures.
12. Background jobs with progress, cancellation, retry, error reporting, and history.
13. Replaceable marketplace, import, export, pricing, grading, and trend adapters.
14. Canonical market-observation history and cross-marketplace comparison read models.
15. Explainable attention, keep/sell, reprice, open/keep-sealed, and marketplace-opportunity signals.
16. Mission Control, Collection Overview, Market Compass, Collector Pulse, Portfolio, and Reports workspaces.
17. Reusable line, bar, stacked-bar, pie/donut, heat-map, daily-volume, sentiment, and sparkline components.
18. Notification and operational task center.
19. Diagnostics bundle, structured logging, version manifest, and support tooling.
20. Architecture enforcement in CI and mandatory repository checkpoints.

## Approved experience direction

### Business Mode

Focus on profit, ROI, cash tied up, inventory age, sell-through, listing readiness, fees, shipping, settlement, and marketplace net proceeds.

### Collector Mode

Focus on collection value, watchlists, allocation, set completion, scarcity, grading potential, market movement, and sealed-product decisions.

The application remembers or explicitly switches modes while using the same underlying products, inventory, observations, and evidence.

### Default overview

The default view should remain simple:

- ranked Needs Attention queue
- collection or inventory value trend
- marketplace net-proceeds comparison
- allocation composition
- freshness and confidence indicators

Heat maps, volume, sentiment, Google Trends, detailed evidence, and additional metrics remain available through expansion or dedicated workspaces.

## Approved market-intelligence direction

- Normalize eBay, TCGplayer, Collectr, PSA, local/manual activity, and future sources through replaceable adapters.
- Treat Google Trends as normalized relative search interest, never as absolute demand proof.
- Prefer net proceeds and liquidity over the highest visible listing price.
- Store source, observed time, import time, confidence, freshness, sample size, and evidence identity.
- Never allow external adapters to write directly to canonical business-authority tables.
- Never issue unexplained Buy, Sell, Keep, Open, or Keep Sealed recommendations.

## Execution rule

Work proceeds in small, reviewable, gated changes. Each material change must preserve the current working application, add focused tests, pass applicable CI and packaging gates, and update repository-backed checkpoint evidence.
