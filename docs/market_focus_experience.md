# MarketDEX Focused Market Experience

## Product principle

MarketDEX must be feature-rich without forcing the operator to interpret every available metric. The default experience presents decisions first, supporting evidence second, and raw metrics only on demand.

## Default information hierarchy

### 1. What needs attention now

The first visible region is a ranked action queue. Each item must answer:

- What changed?
- Why does it matter?
- How urgent is it?
- Which asset, product, set, or marketplace is affected?
- What is the safest next action?

Default priority levels are Critical, Watch, Opportunity, and Informational.

### 2. Market pulse

The market pulse is limited to the smallest set of decision-driving indicators:

- tracked portfolio value and change
- realized and estimated margin
- inventory exposure by product, set, and marketplace
- sell-through velocity
- price movement and spread divergence
- stale or missing market data

### 3. Marketplace comparison

Every supported marketplace contributes through one normalized marketplace adapter and one comparison read model. The default comparison shows:

- current market price
- recent sold price
- available supply or listing count when known
- estimated net proceeds after fees, shipping, and packaging
- sell-through or liquidity signal
- data freshness and confidence

Marketplace-specific details remain available through drill-down views.

### 4. Visual evidence

Charts are selected by the decision they support:

- line chart: price, value, margin, and velocity over time
- grouped bar chart: marketplace price, fees, net proceeds, or sales comparison
- stacked bar chart: inventory or revenue composition over time
- donut chart: current portfolio, inventory, marketplace, or category allocation
- heat map: product or set movement and attention intensity
- sparkline: compact directional context beside a ranked item

Pie or donut charts must represent composition only. They must not be used for time-series or precise comparison.

### 5. Details on demand

Raw metrics, calculation inputs, transaction evidence, listings, history, and audit information remain available below the summary or in dedicated workspace drill-downs. They do not compete with the primary action queue.

## Proposed workspace model

### Mission Control

- ranked attention queue
- five or fewer primary KPIs
- market pulse trend
- marketplace opportunity summary
- data freshness and system health

### Market Compass

- cross-marketplace price and net-proceeds comparison
- movement, liquidity, spread, and confidence signals
- product, card, set, and sealed-product filters

### Collector Pulse

- watchlists
- meaningful movement alerts
- unusual supply or demand changes
- tracked set and product summaries

### Portfolio

- value and cost basis
- realized and unrealized performance
- exposure and concentration
- allocation donut and historical value trend

### Reports

- detailed business and collector analysis
- marketplace, inventory, sales, settlement, and tax read models

## Architecture boundaries

- Marketplace adapters normalize external or imported observations; they never write directly to business-authority tables.
- Market observations retain source, observed time, imported time, confidence, and freshness.
- Decision signals are derived by read models and are not independent business authority.
- Every alert is deterministic, explainable, dismissible, and traceable to evidence.
- The application composition root owns shared marketplace catalogs, signal services, settings, jobs, and workspace module construction.
- UI widgets consume view models or read models rather than querying SQLite directly.

## Recommended implementation sequence

1. Complete the application composition root and feature dependency contract.
2. Add marketplace and market-observation contracts without network dependencies.
3. Add a normalized cross-marketplace comparison read model.
4. Build a deterministic attention-ranking service.
5. Add a focused Mission Control view model.
6. Add reusable chart components and visual-state contracts.
7. Add marketplace adapters incrementally, starting with CSV/manual data and preserving offline-first behavior.
8. Add background refresh jobs only after settings, credentials, diagnostics, and retry behavior are established.
