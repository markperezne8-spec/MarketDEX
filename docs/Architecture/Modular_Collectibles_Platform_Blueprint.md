# MarketDEX Modular Collectibles Platform Blueprint

**Status:** Approved architecture planning authority  
**Delivery priority:** Excellent Windows desktop application  
**Future compatibility:** iOS, Android, and web clients may reuse the platform later

## Goal

Build one modular MarketDEX platform that can grow from effortless Pokémon TCG selling into a broader collectibles operating system without creating duplicate shells, databases, business rules, or category-specific applications.

The architecture should make new features easier to add while keeping the visible experience understandable.

## Architecture shape

```text
┌─────────────────────────────────────────────────────────────┐
│ Windows Desktop Presentation                               │
│ PySide6 workspaces, widgets, view models, navigation       │
└──────────────────────────────┬──────────────────────────────┘
                               │ commands / queries / read models
┌──────────────────────────────▼──────────────────────────────┐
│ Application Layer                                           │
│ use cases, workflows, orchestration, permissions, events    │
└──────────────────────────────┬──────────────────────────────┘
                               │ domain contracts
┌──────────────────────────────▼──────────────────────────────┐
│ Domain Layer                                                │
│ products, ownership, money, policies, decisions, history   │
└──────────────────────────────┬──────────────────────────────┘
                               │ ports / protocols
┌──────────────────────────────▼──────────────────────────────┐
│ Infrastructure Adapters                                    │
│ SQLite, CSV, files, marketplaces, trends, grading, AI      │
└─────────────────────────────────────────────────────────────┘
```

The desktop UI may depend on application contracts. Domain and application rules must not depend on PySide6 widgets, Windows dialogs, tab indexes, or direct SQLite calls.

## Composition and startup

MarketDEX should have:

- one application composition root
- one root `launcher.py`
- one authoritative `MainWindow`
- one `ApplicationComposition`
- one workspace registry
- one feature/module catalog
- one database manager and schema authority
- one migration runner
- one settings composition
- one job system
- one diagnostics/version manifest

The composition root creates shared services and passes explicit dependencies to modules. Modules must not discover dependencies through global variables, hidden window attributes, or import-time side effects.

## Module contract

Each module should eventually declare a stable contract similar to:

```text
ModuleDefinition
- module_id
- version
- dependencies
- commands
- queries
- events
- repositories/providers required
- workspace contributions
- settings contributions
- background jobs
- diagnostics
- install/start/stop lifecycle
```

The catalog validates duplicate IDs, missing dependencies, dependency cycles, and installation order before modifying the UI or database.

## Core module families

### Shared platform modules

- Identity and versioning
- Settings and policies
- Audit and history
- Jobs and notifications
- Diagnostics and logging
- Import/export
- AI command gateway

### Collectibles business modules

- Catalog
- Purchases and Receiving
- Inventory
- Collection
- Pricing
- Market Data
- Listings
- Orders and Fulfillment
- Sales and Settlement
- Portfolio
- Attention
- Research
- Reports and Insights

### Extension modules

- Pokémon TCG
- generic TCG
- future named TCG packs
- graded collectibles
- sealed-product analysis
- Funko Pop
- future gaming collectible packs
- marketplace adapters
- grading/population providers
- trends and attention providers

An extension may contribute fields, validators, product parsers, views, calculations, and provider mappings. It may not create a second inventory authority or duplicate core commercial workflows.

## Domain model boundaries

### Catalog truth

Catalog describes what a product is:

- stable product identity
- category
- game/product line
- franchise/brand
- set/release
- product type and product form
- variant/edition/language/finish
- manufacturer identifiers and external mappings
- contents or bill-of-contents relationships

### Ownership truth

Ownership describes what the user owns and why:

- Inventory Position for business intent
- Collection Position for collector intent
- quantity and unit identity
- cost layers
- condition and grading
- location and custody
- age and business state
- lineage and transformations

Portfolio is a read model over ownership. It never becomes a second ownership database.

### Commercial truth

Commercial modules preserve distinct events:

- Purchase
- Receiving
- Listing
- Sale
- Order
- Shipment
- Delivery/Exception
- Settlement
- Return/Refund/Cancellation

These events may relate to each other, but must not be collapsed into one status field.

### Market truth

Market Data preserves:

- raw observations
- standardized metrics
- derived signals
- recommendations
- user decisions
- actions and outcomes

External observations remain separate from owned inventory and financial authority.

## Identity and future synchronization readiness

Current desktop work remains local-only, but permanent identities should avoid future collision.

Recommended pattern:

- stable machine-readable entity ID generated by the application
- separate human-readable display ID such as `INV-000001`
- immutable creation timestamp
- update/version metadata
- source and provenance metadata
- explicit schema and contract version

No cloud sync is required now. Future synchronization may use a change journal or outbox. Current desktop performance and simplicity remain the priority.

## Commands, queries, and events

### Commands

Commands change authoritative state and must validate permissions, invariants, and evidence.

Examples:

- AddInventoryPosition
- MoveInventory
- RecordPurchase
- CompleteReceiving
- PrepareListing
- PublishListingEvidence
- RecordSale
- CreateOrder
- RecordShipment
- RecordSettlement
- ChangeCollectionIntent
- RecordMarketObservation
- CreateBackup

### Queries

Queries return serializable read models optimized for a screen or AI tool.

Examples:

- GetMissionControlOverview
- GetCollectionOverview
- CompareMarketplaces
- GetListingReadiness
- GetSealedOpenAnalysis
- GetAttentionQueue
- GetPortfolioAllocation

### Events

Events communicate facts after successful state changes.

Examples:

- InventoryPositionAdded
- ListingPrepared
- SaleRecorded
- SettlementVerified
- MarketObservationImported
- AttentionSignalRaised
- CollectionIntentChanged

Events should not become hidden business authority. They represent facts produced by authoritative commands.

## Read-model architecture

Operational screens and charts should read from dedicated, reproducible read models rather than joining arbitrary tables inside widgets.

Read models should expose:

- metric definition
- period and comparison period
- source coverage
- observed/imported timestamps
- freshness status
- confidence/evidence support
- contributing records
- calculation/rule version
- drill-down identity

This allows desktop widgets, future web/mobile clients, exports, and AI tools to consume the same meaning.

## Marketplace and provider architecture

```text
External Source
      ↓
Source Adapter
      ↓
Raw Observation / Import Staging
      ↓
Validation and Product Matching
      ↓
Normalized Market Observation
      ↓
Read Models and Attention Policies
```

Adapters must be replaceable and may not write directly to Inventory, Collection, Sales, or Settlement authority.

Initial adapter progression:

1. manual entry
2. controlled CSV import
3. official export import
4. authorized official API
5. scheduled background refresh where permitted

Uncontrolled scraping is not part of the permanent foundation.

## AI architecture

AI is an authorized application client, not a database administrator.

AI access should use:

- named read tools backed by approved queries
- named write tools backed by approved commands
- permission and confirmation policies
- evidence-linked responses
- confidence and freshness indicators
- audit records for consequential proposals/actions
- deterministic calculators for money and business rules

AI may prepare or recommend. It must not bypass the user, validation, data authority, or external-service permissions.

## Desktop presentation architecture

The current desktop app should favor:

- one shell with registered workspaces
- view models/controllers between widgets and services
- shared selection and context events
- reusable chart components
- consistent toolbar/filter patterns
- keyboard and mouse productivity
- accessible labels and non-color-only status
- progressive disclosure
- saved views and remembered mode
- task progress without UI freezing

Business Mode and Collector Mode adjust emphasis and available shortcuts; they do not create separate data stores.

## Visual and decision architecture

Every primary screen should answer:

1. What changed?
2. Why does it matter?
3. How fresh and reliable is the evidence?
4. What deserves attention?
5. What can the user do next?

The UI hierarchy should be:

```text
Decision / Attention
        ↓
Explanation and comparison
        ↓
Supporting chart
        ↓
Evidence table and history
```

Charts require a clear business question and metric owner. Raw details remain accessible without dominating the default view.

## Persistence and migration architecture

Only canonical persistence infrastructure may open SQLite connections or create/alter tables.

Each schema change requires:

- schema version
- deterministic forward migration
- pre-migration backup
- transaction where supported
- validation before commit
- restart reconstruction test
- historical database fixture
- rollback/recovery plan
- migration record/checksum
- release note

Read models may be rebuilt. Business evidence and audit history must not be silently discarded.

## Settings and secrets separation

Separate:

- user preferences
- business policies and thresholds
- marketplace assumptions
- runtime state
- credentials/secrets
- feature enablement

Secrets must not be stored in logs, exported diagnostics, or plain configuration files without an approved secure-storage strategy.

## Background work

Long-running imports, backups, report generation, market refreshes, image processing, and exports should use one job framework supporting:

- queued/running/succeeded/failed/cancelled states
- progress and current step
- cancellation where safe
- retry policy
- error details
- start/end timestamps
- source and initiating user/action
- job history
- completion notification

## Diagnostics and supportability

A diagnostics bundle should eventually include:

- app and schema versions
- enabled modules and adapters
- migration history
- workspace/feature registry state
- recent sanitized errors
- job failures
- backup health
- provider freshness/health
- operating environment

It must exclude credentials and sensitive user data unless the user explicitly includes a controlled sample.

## Mandatory gates

Applicable work must pass:

1. Authority
2. Architecture
3. Behavior
4. Data and Migration
5. UX and Accessibility
6. Integration and Provenance
7. Platform Compatibility
8. AI Safety
9. Packaging and Installed Runtime
10. Release and Checkpoint

Additional module-specific gates may be added, but may not weaken these foundations.

## Recommended implementation order

1. Finish and reconcile shell/composition/market-intelligence stack.
2. Establish canonical persistence and migration authority.
3. Reconcile competing legacy trees and direct database access.
4. Formalize module, command, query, event, and repository contracts.
5. Add view-model/controller and shared selection architecture.
6. Build Collection Overview and mode toggle from read models.
7. Add canonical market-observation persistence and import staging.
8. Add attention policies and explanation read models.
9. Add marketplace CSV/manual adapters.
10. Add settings, jobs, backups, diagnostics, and version manifest.
11. Extend selling workflow through orders, shipping, and settlement.
12. Add category packs without changing shared business authority.
13. Add controlled AI tools over stable queries and commands.
14. Consider future clients only after desktop product quality and reusable contracts are proven.

## Architecture decision rule

A new feature belongs in MarketDEX when it:

- answers a meaningful user or business question
- has one clear authority owner
- fits an existing module or justifies a new module
- can be tested independently
- does not create a competing data path
- preserves historical evidence
- remains understandable in the UI
- declares platform and AI impact
- passes its mandatory gates

When two designs provide similar value, choose the simpler design that preserves future extension.
