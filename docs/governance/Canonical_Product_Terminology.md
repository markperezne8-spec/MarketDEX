# MarketDEX Canonical Product Terminology

**Status:** Approved naming authority for new user-facing work  
**Purpose:** Prevent overlapping names, duplicate concepts, and confusing labels as MarketDEX grows.

## Naming principles

- One user-facing name per concept.
- Different concepts must not share the same primary label.
- User-facing labels should be plain and action-oriented.
- Internal names may be more technical but must map to one canonical product term.
- Legacy names may remain temporarily as migration aliases; they must not create a second authority.
- Stable IDs use lowercase kebab-case or snake_case and must not depend on tab order or widget position.

## Canonical workspace names

| Canonical user-facing name | Meaning | Names to avoid or treat as legacy |
|---|---|---|
| **Mission Control** | Default cross-business decision and attention overview | Dashboard, Home Dashboard, Command Center when referring to the main app home |
| **Inventory** | Business-owned items held for sale, transformation, grading, or operational use | Asset Manager as a primary user-facing workspace |
| **Collection** | Personally held items governed by collector intent | Personal Collection as a competing workspace name |
| **Pricing** | Selected-item pricing, costs, margins, and net-proceeds decisions | Price Tool, Profit Tool as separate top-level workspaces |
| **Listings** | Listing preparation, readiness, marketplace selection, publishing evidence, and listing history | Listing Workflow as a competing user-facing top-level name; it may remain an internal/legacy ID during migration |
| **Orders & Shipping** | Fulfillment responsibilities, packing, shipping, delivery, and exceptions | Shipping as a separate disconnected top-level system |
| **Sales & Settlement** | Sales, fees, payouts, settlement evidence, and true outcomes | Sales, Payouts, and Settlement as unrelated authorities |
| **Market Compass** | Cross-marketplace comparison, price spread, liquidity, supply, and realistic net proceeds | Marketplace Dashboard, Platform Analysis |
| **Collector Pulse** | Watchlists, price movement, daily volume, sentiment, scarcity, search attention, and notable changes | Market Pulse when it would conflict with Market Compass |
| **Research Lab** | Deep research, grading analysis, hypotheses, experiments, and evidence review | Research Center, Research Hub as parallel names |
| **Portfolio** | Analytical value, allocation, concentration, and performance across owned positions | Portfolio as a second inventory or collection database |
| **Reports & Insights** | Detailed historical analysis, exports, and supporting evidence | Analytics as a separate user-facing authority |
| **Settings** | Preferences, policies, integrations, backups, diagnostics, and maintenance | Administration as the normal daily user label |

## Canonical capability names

| Canonical term | Definition | Important distinction |
|---|---|---|
| **Attention Engine** | Internal capability that ranks risks, opportunities, blockers, and stale evidence | Not a workspace and not a notification delivery system |
| **Needs Attention** | User-facing ranked queue produced by the Attention Engine | Use this instead of Alerts Center or Attention Center |
| **Task Center** | User-facing long-running jobs and operational tasks with progress, retry, and history | Tasks are work; attention signals are reasons to review |
| **Notification** | A delivery message about a completed job, exception, or important signal | Notifications do not own business state |
| **Market Intelligence** | Shared domain/application capability for market observations and derived analysis | User-facing exploration is divided into Market Compass, Collector Pulse, and Research Lab |
| **Business Mode** | A presentation lens emphasizing selling, profit, capital, and operations | Not a separate Business module or database |
| **Collector Mode** | A presentation lens emphasizing collection goals, value, scarcity, and holding decisions | Not a separate collection database |
| **Business Operations** | The combined purchasing, inventory, listing, orders, sales, settlement, and capital workflow | Use this when older documents say only “Business” as a module |

## Product and ownership terminology

| Canonical term | Definition |
|---|---|
| **Product** | Canonical catalog identity describing what an item is, independent of ownership |
| **Product Variant** | A meaningful edition, printing, language, finish, size, grade, packaging, or other identity distinction |
| **Owned Item** | Plain user-facing umbrella term for something the user owns |
| **Inventory Position** | Business ownership state: product, quantity, cost layers, location, condition, age, and operational intent |
| **Collection Position** | Collector ownership state: product, quantity, acquisition evidence, goals, favorites, never-sell intent, and willingness to trade/sell |
| **Lot** | An acquisition or grouped quantity with shared purchase evidence; not necessarily one product |
| **Asset** | Allowed as an internal accounting or legacy umbrella term, but avoid as the primary UI label because it overlaps Inventory and Collection |
| **Item** | Contextual UI word only; it does not replace canonical Product or Position identities in storage and APIs |

## Category terminology

| Canonical term | Definition | Example |
|---|---|---|
| **Collectible Category** | Broad family of collectible | Trading Card Game, Vinyl Figure, Gaming Collectible |
| **Game or Product Line** | Specific game/line within a category | Pokémon TCG, Magic: The Gathering, One Piece Card Game, Funko Pop |
| **Franchise or Brand** | Intellectual property or commercial brand when relevant | Pokémon, Disney, Marvel, Funko |
| **Set or Release** | Defined release grouping | Pokémon set, Funko series/wave |
| **Product Type** | Physical/commercial form | Single Card, Booster Pack, ETB, Booster Box, Slab, Funko Pop |
| **Product Form** | Operational unit and state relevant to quantity and transformation | Sealed Box, Pack, Raw Card, Graded Card, Opened Contents |

Category-specific fields belong to explicit category extensions. They must not be forced into every product or duplicated in separate application trees.

## Market terminology

| Canonical term | Definition |
|---|---|
| **Marketplace** | Commercial channel where products may be listed or sold, such as eBay or TCGplayer |
| **Provider / Data Source** | Source that supplies observations, such as Collectr, Google Trends, PSA, CSV, or a marketplace API |
| **Market Observation** | One source-attributed fact or measurement observed at a specific time |
| **Market Metric** | Standardized measurement derived or normalized from observations |
| **Market Signal** | Explainable condition detected from evidence, such as unusual volume or price divergence |
| **Recommendation** | Evidence-linked guidance generated from policies and signals |
| **Decision** | The user's recorded choice |
| **Action** | An executed command or task following a decision |
| **Market Value** | Evidence-based estimate of current value; not automatically realizable proceeds |
| **Listed Price** | Asking price for an active listing |
| **Sold Price** | Price evidenced by a completed sale, before clarifying fees/costs unless explicitly stated |
| **Net Proceeds** | Expected or actual cash after applicable marketplace fees and selling costs, before cost basis unless specified |
| **Net Profit** | Gross revenue minus verified fees, fulfillment costs, and cost basis |
| **Daily Volume** | Count or quantity of qualified sale observations for a defined day, source, and scope |
| **Search Interest** | Relative attention measure such as Google Trends 0–100; not absolute search volume or demand proof |
| **Sentiment** | Composite interpretation of approved evidence; it must expose factors, timeframe, freshness, and confidence |

## Commercial lifecycle terminology

| Canonical term | Definition |
|---|---|
| **Purchase** | Acquisition agreement and financial evidence |
| **Receiving** | Confirmation of what physically arrived and in what condition/quantity |
| **Listing** | Marketplace offer and its preparation/publication state |
| **Sale** | Commercial agreement to transfer products for consideration |
| **Order** | Operational fulfillment responsibility created by a sale |
| **Shipment** | Carrier/transport event and evidence |
| **Delivery** | Evidence that fulfillment reached the recipient or an exception occurred |
| **Settlement** | Marketplace/payment evidence showing payout, deductions, timing, and allocation |
| **Return / Refund / Cancellation** | Explicit corrective commercial events; they must not silently rewrite the original history |

## Decision-language rules

Use these labels for explainable user guidance:

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

Avoid unexplained labels such as BUY NOW, SELL NOW, WINNER, LOSER, HOT, or DEAD. Strong action wording requires explicit evidence, confidence, freshness, and user authority.

## Naming conflict resolutions

1. **Dashboard → Mission Control** for the primary app home.
2. **Platform → Marketplace** when discussing eBay, TCGplayer, or selling channels. “Platform” is reserved for Windows, iOS, Android, and web architecture.
3. **Asset Manager → Inventory or Collection** based on ownership intent.
4. **Business module → Business Operations** to avoid conflict with Business Mode.
5. **Analytics → Reports & Insights** as the user-facing workspace; analytics remains an internal capability.
6. **Alerts / Attention Center → Needs Attention** for ranked signals; use Task Center for jobs and work queues.
7. **Listing Workflow → Listings** as the long-term user-facing label. Existing stable IDs may retain `listing-workflow` until a controlled compatibility migration is approved.
8. **Personal Collection → Collection** unless a sentence needs to distinguish personal intent from business inventory.
9. **Marketplace Dashboard / Platform Analysis → Market Compass**.
10. **Market Pulse → Collector Pulse** when referring to the dedicated watchlist and movement workspace.

## Compatibility rule for existing code and data

Renaming a user-facing concept does not authorize immediate changes to database identifiers, persisted workspace IDs, filenames, import columns, or APIs.

A controlled rename must provide:

- old-to-new mapping
- compatibility alias when necessary
- migration or read fallback for persisted identifiers
- regression tests
- documentation update
- release note
- removal plan for the legacy alias

Clarity improves immediately in new documentation and UI work. Existing identifiers change only through a gated compatibility migration.