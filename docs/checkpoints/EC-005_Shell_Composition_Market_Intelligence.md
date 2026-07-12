# EC-005 — Shell, Composition, Market Intelligence, and Platform Foundation

**Checkpoint date:** 2026-07-11  
**Status:** In progress through stacked draft PRs #164, #165, and #166  
**Authority:** Repository code, merged history, pull-request heads, and GitHub Actions results

## Product Owner approval

The Product Owner approved the architecture and product recommendations consolidated in `docs/governance/Approved_Architecture_Roadmap.md`.

Desktop is the only current delivery target. iOS, Android, and browser clients are future compatibility plans only. Pokémon TCG is the first optimized workflow; shared architecture must remain extensible to other TCGs, sealed gaming products, graded cards, Funko Pops, gaming collectibles, and related collectibles.

## Historical change set

### PR #163 — Shell workspace foundation — merged

- Added `WorkspaceDefinition` and `WorkspaceRegistry`.
- Established one deterministic workspace registration authority.

### PR #164 — Professional shell composition — draft

- Added `WorkspaceHost` as the sole top-level workspace mounting and navigation owner.
- Added canonical Inventory, Pricing, and Listing Workflow identities and order.
- Removed numeric tab navigation and reduced shell wiring ambiguity.

### PR #165 — Application composition root — draft

- Added one `ApplicationComposition` for shared runtime construction.
- Reduced `launcher.py` to startup responsibilities.
- Added stable feature IDs and explicit dependency validation.
- Preserved the existing root launcher and `MainWindow` as sole runtime authorities.

### PR #166 — Market intelligence and governance foundation — draft

- Added Business and Collector mode catalogs.
- Added marketplace capability registry.
- Added normalized market observations.
- Added attention signals with confidence and suggested actions.
- Added visualization definitions for line, bar, pie, heat map, daily volume, sentiment, and sealed-versus-open analysis.
- Added sealed/open and price-per-pack calculation contracts.
- Added a Google Trends-compatible relative-interest provider boundary.
- Attached market intelligence to the canonical application composition.
- Added mandatory architecture gates and repository-backed governance tests.
- Added desktop-first future platform compatibility rules.
- Added safe AI-operation boundaries.
- Added the approved recommendation roadmap.

## Mandatory checkpoint results

| Gate | Result | Evidence |
|---|---|---|
| Authority | PASS | One launcher, one `MainWindow`, one workspace registry, one composition root |
| Architecture | PASS | Stable workspace, feature, marketplace, mode, observation, chart, and platform contracts |
| Behavior | PASS/PENDING | Focused unit and integration tests pass; final stacked CI remains required |
| Data | NOT APPLICABLE YET | Market intelligence foundation is contract-only and adds no schema migration |
| UX | DESIGN CONTRACT PASS | Decision-first, evidence-second, raw-metrics-on-demand rule recorded |
| Integration | FOUNDATION PASS | Provider and adapter boundaries exist; live marketplace integrations are deferred |
| Platform compatibility | FOUNDATION PASS | Domain and application contracts are required to remain presentation-independent; no mobile/web app tree exists |
| AI safety | FOUNDATION PASS | AI must use controlled commands, evidence, permissions, validation, and audit; direct database mutation is forbidden |
| Packaging | PASS ON PRIOR HEAD / REVALIDATION REQUIRED | Windows executable and installer passed before latest governance commits |
| Release | BLOCKED | PRs #164–#166 remain draft and unmerged |

## Approved future architecture backlog

- canonical persistence and migration authority
- legacy tree reconciliation
- dedicated workspace modules
- view models and controllers
- typed command and event architecture
- repository and provider protocols
- settings and business-policy separation
- backup, rollback, and historical upgrade fixtures
- background jobs
- marketplace and trend adapters
- market-history read models
- attention and recommendation engine
- notifications and task center
- diagnostics and version manifest
- architecture enforcement in CI

## Known limitations

- No rendered Collection Overview workspace yet.
- No live Google Trends, marketplace API, or scheduled data refresh yet.
- No persisted market-observation schema yet.
- No active iOS, Android, or web application; those remain future plans.
- No executable AI action interface yet.
- No final release classification until stacked PRs merge and all gates rerun on their final heads.

## Exact resume point

1. Complete final CI for PR #166.
2. Reconcile and merge stacked PRs in order: #164, #165, #166.
3. Update the current foundation checkpoint and checkpoint manifest after merge.
4. Begin the desktop Collection Overview Workspace and Business/Collector Mode Toggle.
5. Before persistence work, design the canonical market-observation schema and migration gate.
6. Continue the approved architecture roadmap through small, gated pull requests.
