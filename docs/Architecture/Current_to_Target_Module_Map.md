# MarketDEX Current-to-Target Module Map

**Status:** Architecture planning baseline  
**Scope:** Classification only; this document does not authorize deletion or relocation  
**Classification:** `KEEP`, `ADAPT`, `MIGRATE`, `RETIRE`, `REVIEW`

## Purpose

Map the current repository into the approved modular architecture without rebuilding proven capabilities or deleting overlapping code by assumption.

- **KEEP** — canonical or proven surface that should remain authoritative.
- **ADAPT** — proven capability that should gain interfaces, composition, tests, or module boundaries without behavioral rebuild.
- **MIGRATE** — capability should move behind a target module contract through compatibility-preserving steps.
- **RETIRE** — confirmed obsolete surface may be removed only after replacement, reference, and compatibility evidence.
- **REVIEW** — authority or usage is unclear; repository evidence is required before classification changes.

## Runtime and shell

| Current surface | Classification | Target responsibility | Notes |
|---|---|---|---|
| root `launcher.py` | KEEP / ADAPT | Desktop bootstrap | Remains the sole entry point; should stay thin and delegate construction to composition. |
| root `ui/main_window.py` | KEEP / ADAPT | Desktop shell | Remains the sole authoritative top-level window. |
| `composition/application_composition.py` | KEEP / ADAPT | Application composition root | Draft-stack target for shared services, modules, settings, jobs, and diagnostics. |
| `composition/feature_catalog.py` | KEEP / ADAPT | Module/feature dependency catalog | Evolve from installer ordering into explicit module lifecycle without changing behavior blindly. |
| `ui/workspace_contract.py` | KEEP | Workspace contribution contract | Stable user-facing workspace identity and factory boundary. |
| `ui/workspace_registry.py` | KEEP | Workspace registration authority | One deterministic registry. |
| `ui/workspace_host.py` | KEEP / ADAPT | Workspace mounting and navigation | Presentation-only host; no business authority. |
| `ui/shell_workspace_catalog.py` | KEEP / ADAPT | Canonical desktop workspace catalog | User-facing labels should follow `Canonical_Product_Terminology.md`. |
| `ui/main_window_m23.py`, `ui/main_window_m24.py` | REVIEW | Historical/legacy shell evidence | Do not promote. Retire only after references, packaging, and migration evidence prove they are unused. |
| `app/ui/main_window.py`, `app/ui/app_shell/*` | REVIEW / MIGRATE | Legacy presentation tree | Extract unique proven behavior into the root shell or target workspaces; do not create a second active app. |

## Persistence and database authority

| Current surface | Classification | Target responsibility | Notes |
|---|---|---|---|
| `core/schema.py` | KEEP / ADAPT | Canonical schema and migration authority | Preserve existing verified schema responsibilities; separate schema definition from ordered migrations over time. |
| `core/database_manager.py` | KEEP / ADAPT | Canonical SQLite connection/transaction boundary | Only approved persistence infrastructure should open runtime SQLite connections. |
| `core/runtime_database_migration.py` | KEEP / ADAPT | Upgrade coordinator | Add backup, transactional validation, history, checksums, rollback/recovery, and historical fixtures. |
| root `repositories/*` | KEEP / ADAPT | Module repository implementations | Preserve mature authority; add protocols and module ownership gradually. |
| `app/database/database_manager.py` | REVIEW / MIGRATE / RETIRE | Competing legacy database path | Compare unique behavior; route any required capability to canonical infrastructure before retirement. |
| `app/database/migrations.py` | REVIEW / MIGRATE / RETIRE | Legacy migration path | Must not remain a competing schema authority. |
| `app/repositories/*` | REVIEW / MIGRATE / RETIRE | Legacy repository tree | Extract unique interfaces/behavior only after evidence review. |
| services that call `sqlite3.connect` directly | REVIEW / MIGRATE | Canonical repositories | Replace private connections with injected repository/database authority. CAP-005B is a priority example. |

## Catalog and product identity

| Current surface | Classification | Target responsibility | Notes |
|---|---|---|---|
| `services/product_registry_service.py` | KEEP / ADAPT | Catalog application service | CAP-005 is Partial; extend existing logic rather than rebuild. |
| product-aware lifecycle services | KEEP / ADAPT | Catalog integrations | Preserve `product_id` and existing authority; add explicit module boundaries. |
| source/product mapping and bill-of-contents structures | REVIEW / ADAPT | Catalog adapters and relationships | Preserve source identity, versioning, and lineage. |
| Pokémon-specific parsing/rules | MIGRATE | Pokémon TCG category extension | Shared Product/Variant/Set concepts remain category-neutral. |

## Inventory and collection

| Current surface | Classification | Target responsibility | Notes |
|---|---|---|---|
| `services/inventory_app_service.py` | KEEP / ADAPT | Inventory application service | Mature capability; expose commands/queries and remove UI coupling. |
| `services/inventory_service.py` | KEEP / ADAPT | Inventory domain/application policy | Preserve proven rules and regression evidence. |
| `repositories/inventory_repository.py` | KEEP / ADAPT | Inventory repository implementation | Add protocol and transaction boundary; do not rebuild. |
| root inventory UI feature modules | MIGRATE | Inventory workspace module | Move feature composition behind a dedicated module/workspace contract gradually. |
| `app/ui/` collection surfaces | REVIEW / MIGRATE | Collection workspace | CAP-006 is Missing in permanent root authority; reuse visual/proven ideas only after evidence classification. |
| future Collection service/repository | NEW CONTROLLED SLICE | Collection module | Must share Catalog and ownership conventions without duplicating Inventory. |

## Pricing, listings, and selling operations

| Current surface | Classification | Target responsibility | Notes |
|---|---|---|---|
| `ui/inventory_cost_feature.py` | KEEP / MIGRATE | Pricing workspace/controller | Preserve calculation behavior; migrate installer wiring, not business meaning. |
| `ui/inventory_profit_feature.py` | KEEP / MIGRATE | Pricing module | Deterministic economics remain normal code. |
| `ui/inventory_price_guidance_feature.py` | KEEP / MIGRATE | Pricing module | Recommendations require evidence/freshness/confidence where market data is used. |
| listing-plan repositories/services | KEEP / ADAPT | Listings module | CAP-003 is Complete; preserve behavior and focused tests. |
| listing UI feature chain | KEEP / MIGRATE | Listings workspace | Long-term user-facing label is `Listings`; retain stable legacy IDs until gated migration. |
| sale-completion feature | KEEP / ADAPT | Sales & Settlement workflow | Preserve authority boundaries among Sale, Order, Shipment, and Settlement. |
| order, fulfillment, shipment, and closure services | KEEP / ADAPT | Orders & Shipping module | Group by business responsibility; do not flatten events into one status. |
| settlement and allocation services/repositories | KEEP | Sales & Settlement module | CAP-008 through CAP-011 are proven authority and must not be rebuilt. |

## Mission Control, attention, and reporting

| Current surface | Classification | Target responsibility | Notes |
|---|---|---|---|
| `services/mission_control_service.py` | KEEP / ADAPT | Mission Control read model/service | Canonical root projection; preserve exact authority and read-only behavior. |
| `services/dashboard_service.py` | REVIEW / MIGRATE / RETIRE | Legacy broader dashboard evidence | Do not promote as competing Mission Control authority. Extract only uniquely justified read models. |
| root Mission Control UI | KEEP / ADAPT | Mission Control workspace | Use canonical user-facing name; progressive disclosure and Needs Attention ranking. |
| `app/ui/mission_control/*`, `app/ui/pages/mission_control.py` | REVIEW / MIGRATE / RETIRE | Legacy visual/behavior evidence | Compare against root authority before reuse. |
| future Attention Engine | NEW CONTROLLED MODULE | Attention module | Consumes approved read models; does not own underlying business facts. |
| existing attention/advisory services | REVIEW / ADAPT | Attention policies | Consolidate explainable, non-duplicative policies after evidence inventory. |
| report surfaces | REVIEW / NEW CONTROLLED SLICE | Reports & Insights | CAP-012 is Missing in permanent root authority. |

## Market intelligence

| Current surface | Classification | Target responsibility | Notes |
|---|---|---|---|
| `market_intelligence/*` contracts | KEEP / ADAPT | Market Data and Attention foundations | Contract-only foundation; persistence and live adapters remain pending. |
| marketplace registry | KEEP / ADAPT | Integration capability catalog | Marketplace is the commercial term; Platform is reserved for OS/client architecture. |
| normalized `MarketObservation` | KEEP / ADAPT | Market Data domain contract | Add raw staging, persistence, provenance, product matching, and historical read models later. |
| Google Trends provider boundary | KEEP / ADAPT | Search-attention adapter | Relative interest only; preserve query, geography, timeframe, freshness, and source. |
| sealed-versus-open calculator | KEEP / ADAPT | Research/Pricing decision service | Deterministic inputs, uncertainty, and evidence explanation required. |

## Settings, jobs, integrations, and diagnostics

| Current surface | Classification | Target responsibility | Notes |
|---|---|---|---|
| scattered settings/constants | REVIEW / MIGRATE | Settings and Policies module | Separate user preference, business policy, secret, feature flag, and runtime state. |
| imports/exports | REVIEW / ADAPT | Integration adapters and jobs | Add staging, preview, validation, duplicate handling, and audit. |
| logging/runtime diagnostics | REVIEW / ADAPT | Diagnostics module | Structured, sanitized logs and exportable support bundle. |
| direct long-running UI work | REVIEW / MIGRATE | Job system | Central progress, cancellation, retry, history, and notifications. |
| marketplace-specific logic inside UI/services | REVIEW / MIGRATE | Replaceable marketplace adapters | External adapters never write canonical business tables directly. |

## AI-facing architecture

| Current/future surface | Classification | Target responsibility | Notes |
|---|---|---|---|
| AI reading arbitrary database/files | RETIRE / FORBID | Approved queries/read models | No direct authority access. |
| AI-generated recommendations | ADAPT | Explainable AI assistance | Evidence, freshness, confidence, and rule/model version required. |
| AI write actions | NEW CONTROLLED SURFACE | Command gateway | Uses the same commands, permissions, validation, confirmation, and audit as people. |
| deterministic calculations | KEEP AS NORMAL CODE | Domain/application services | AI may explain results but does not replace money/business calculations. |

## Documentation and evidence

| Current surface | Classification | Target responsibility | Notes |
|---|---|---|---|
| `Vision.md`, `WorkbookBlueprint.md`, Constitution/standards | KEEP | Product/business authority | Preserve approved business knowledge. |
| `FoundationCheckpoint.md` | KEEP | Current state and resume authority | Update at each material checkpoint. |
| `CheckpointManifest.md` | KEEP | Completed historical index | Do not record draft work as delivered. |
| EC checkpoint files | KEEP | Detailed in-progress evidence | Latest EC supplies current change evidence. |
| `Capability_Matrix.md` | KEEP / ADAPT | Derived capability status | Update only from merged repository and verification evidence. |
| `Repository_Reconciliation.md` | KEEP / ADAPT | Current implementation authority map | Update after stacked changes merge; draft target maps do not overwrite main truth. |
| overlapping or generated-looking service families | REVIEW | Evidence classification | Naming or apparent duplication is not sufficient deletion authority. |

## Migration waves

### Wave 1 — Preserve authority

- finish shell/composition stack
- enforce one persistence path
- document names and module ownership
- repair required gates

### Wave 2 — Add contracts around proven behavior

- repository protocols
- command/query/event definitions
- view models/controllers
- read-model boundaries

### Wave 3 — Reconcile legacy trees

- compare root and `app/` surfaces file by file
- migrate unique proven behavior
- add compatibility aliases/tests
- retire only after reference and runtime evidence

### Wave 4 — Add missing vertical slices

- Collection
- Reports & Insights
- Market Data persistence
- Attention Engine

### Wave 5 — Extend operations and integrations

- jobs, settings, backups, diagnostics
- manual/CSV marketplace adapters
- orders/shipping/settlement UX
- category extension packs
- controlled AI tools

## Rule

`Complete` capabilities are preserved and adapted, not rebuilt. `Partial` capabilities are extended through their existing authority. `Missing` capabilities receive one small verified vertical slice. `Review` surfaces are never deleted by assumption.