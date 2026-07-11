# EC-009 — Current UI Audit and First Visual Primitives

**Checkpoint date:** 2026-07-11  
**Status:** Phase 1 audit and first reusable PySide primitives complete; production Mission Control adoption remains next  
**Branch:** `agent/market-intelligence-foundation`  
**Pull request:** Draft PR #166  
**Head at checkpoint creation:** `b6d4532bd8ae05c5d09092e3b8b180e9ff930a5d`  
**Related asset gate:** Issue #167

## Purpose

Begin the real implementation stage behind the approved gamified Visual North Star without performing a broad UI rewrite or changing authoritative business behavior.

## Current UI audit completed

Added:

`docs/design/CURRENT_UI_COMPONENT_AUDIT.md`

The audit classifies current presentation surfaces using `KEEP`, `ADAPT`, `MIGRATE`, `RETIRE`, and `REVIEW`.

### Key findings

- root `ui/main_window.py` is authoritative and behavior-rich but owns too many presentation responsibilities
- `ui/workspace_host.py` has stable registry-based behavior but a transitional hard-coded light tab presentation
- `ui/viewport_fit_feature.py` preserves useful workspace separation but mixes composition, styling, method wrapping, and compatibility aliases
- root Inventory, Pricing, Listings, and sale-completion feature modules contain proven behavior that must be visually migrated rather than rebuilt
- `app/ui/themes/theme.qss` and `app/ui/themes/theme_manager.py` are competing legacy theme surfaces and may not become a second theme authority
- `app/ui/widgets/md_dashboard_card.py` contains useful historical intent but is too limited to become the canonical KPI component directly
- legacy Mission Control pages use static values and may not become production authority
- existing tables and dialogs should preserve behavior while moving to reusable components
- no authoritative gamification domain exists yet; trainer progress, badges, quests, and achievements remain future capability foundations

## First implementation slice selected

**Mission Control Header + KPI Card Foundation**

This slice was chosen because it:

- creates high visual impact
- reuses the existing canonical Mission Control snapshot
- requires no schema change
- proves tokens and components with real data
- establishes patterns reusable by Inventory, Collection, Market Compass, and Reports
- preserves current routes and business workflows

## First concrete PySide foundations

### Qt theme adapter

Added:

`ui/design_system/qt_theme.py`

Responsibilities:

- translate semantic tokens into canonical Qt stylesheet selectors
- style shell surfaces, headers, panels, KPI cards, badges, buttons, inputs, tables, headers, focus, tooltips, and scrollbars
- remain independent from services, repositories, and database logic

### Reusable PySide components

Added:

`ui/design_system/widgets.py`

Initial components:

- `MarketDEXWorkspaceHeader`
- `MarketDEXKpiCard`
- `MarketDEXStatusBadge`
- `MarketDEXDashboardPanel`
- `MarketDEXStatePanel`

The components include stable object names, accessible names, semantic states, and no business-service dependency.

### Tests

Added:

`tests/test_qt_design_system_primitives.py`

The tests protect:

- semantic QSS generation
- required component selectors
- token use
- component availability
- independence from services, repositories, and SQLite

## Brand-asset transition

`branding/asset_manifest.py` now distinguishes:

- approved active v1 Visual North Star identity
- historical v0 compatibility asset
- permanent official mascot
- current required package assets
- approved assets pending synchronization

The active v1 resolver fails visibly while the binary is missing rather than silently using a substitute.

Issue #167 records the exact binary synchronization requirement and acceptance criteria.

## Protected behavior

No change was made to:

- Mission Control snapshot fields or calculations
- Inventory commands or selection behavior
- Pricing calculations
- Listing readiness or publication behavior
- sale, order, shipment, or settlement authority
- database schema or migrations
- root launcher and MainWindow authority
- workspace IDs
- executable or installer entry paths

## Gate status

| Gate | Result | Evidence |
|---|---|---|
| Vision Continuity | PASS | Active direction and implementation phase preserved in repository authority |
| Visual Identity | PASS FOR FOUNDATION | Active v1 and mascot identities remain explicit |
| Design System | PASS FOR FIRST PRIMITIVES | Theme adapter and reusable PySide components added |
| Current UI Audit | PASS | Root and legacy surfaces classified with migration guidance |
| Architecture | PASS FOR FOUNDATION | Components have no business or persistence dependency |
| Accessibility | FOUNDATION PASS | Accessible names, focus selectors, and state requirements established |
| Behavior | NOT CHANGED | No production business workflow changed |
| Data | NOT CHANGED | No schema or persisted state changed |
| Active v1 Binary Asset | BLOCKED / TRACKED | Issue #167 remains open |
| Mission Control Adoption | PENDING | First real workspace section has not yet been migrated |
| Packaging | BLOCKED | Active v1 and design assets are not yet verified in packaged/installed runtime |
| Release | BLOCKED | Existing Listing failure and stacked draft conditions remain |

## Exact resume point

1. Synchronize the exact v1 PNG through issue #167.
2. Promote v1 to required source and package authority after identity verification.
3. Apply `build_marketdex_qss()` to a controlled root UI integration point.
4. Replace only the existing Mission Control title and KPI `QGroupBox` surface with `MarketDEXWorkspaceHeader` and `MarketDEXKpiCard` while preserving all existing snapshot keys and refresh behavior.
5. Add focused UI tests for values, accessibility, resizing, and behavior parity.
6. Obtain visual acceptance against the approved v1 image at practical desktop resolutions.
7. Migrate Inventory summary cards and table chrome only after the Mission Control slice passes.
8. Continue canonical domain and persistence architecture in parallel.
9. Return to the known Listing CI failure before any stacked PR is marked ready or merged.
10. Run the full architecture, design-system, behavior, accessibility, package, installer, installed-runtime, and release gates on final heads.

## Continuity rule

The first production use of the new components must consume real existing MarketDEX data. Mock values may appear in documentation or isolated tests only and may not be presented as production truth.