# MarketDEX Current UI and Component Audit

**Status:** Phase 1 audit baseline  
**Date:** 2026-07-11  
**Authority:** Repository evidence on the active architecture branch  
**Classification:** `KEEP`, `ADAPT`, `MIGRATE`, `RETIRE`, `REVIEW`

## Purpose

Map the current desktop presentation into the approved Visual North Star and reusable design-system architecture without rebuilding proven business behavior or deleting legacy surfaces by assumption.

## Executive result

The current root desktop runtime contains proven Inventory, Mission Control, Pricing, Listings, and sale-completion behavior, but presentation responsibilities remain concentrated in `ui/main_window.py` and installer-style feature modules.

The visual layer currently mixes:

- inline widget construction
- inline stylesheets
- light and dark theme fragments
- legacy `app/` UI components
- direct service calls from widgets
- business workflow wiring and presentation composition
- transitional tab-based workspace navigation

The safest path is not a rewrite. The safe path is:

1. preserve authoritative services and workflows
2. introduce semantic token access
3. implement reusable PySide components
4. replace one visual surface at a time
5. keep read models and commands stable
6. retire duplicate theme/UI paths only after reference evidence

## Root runtime shell

### `ui/main_window.py`

**Classification:** `KEEP / ADAPT / MIGRATE`

**Proven value**

- authoritative root `MainWindow`
- Mission Control snapshot rendering
- Inventory table and workflow
- import/export actions
- add, adjust, bulk-adjust, archive, and restore operations
- existing tests and package entry integration

**Current visual/architecture debt**

- large single file owns dialogs, shell, Inventory page, KPI cards, table, actions, service calls, and formatting
- one-line widget construction reduces maintainability
- hard-coded font sizes appear directly in widgets
- `QGroupBox` is used as an undeclared KPI-card system
- no reusable workspace header, KPI card, status badge, state panel, or theme adapter
- no branded shell/header/left navigation
- dialogs use default desktop form styling
- UI calls application services directly instead of using dedicated view models/controllers
- mascot and brand assets are not resolved by production UI
- no explicit responsive layout or high-DPI contract

**Migration direction**

- keep the class as sole shell authority
- move dialogs into Inventory presentation modules
- add view models/controllers without changing service authority
- replace inline KPI `QGroupBox` creation with a reusable KPI card
- replace direct style strings with semantic tokens
- preserve every command, confirmation, and read-model field during visual migration

## Workspace host and navigation

### `ui/workspace_host.py`

**Classification:** `KEEP / ADAPT`

**Strengths**

- stable workspace IDs
- registry-driven mounting
- deterministic navigation
- accessible host name
- clear ownership of activation and lookup

**Debt**

- visual presentation is a hard-coded light tab stylesheet
- tab navigation does not match the approved persistent left navigation
- colors, spacing, radii, and states bypass semantic tokens
- no collapsed/expanded navigation model

**Migration direction**

- preserve registry, mounting, activation, and stable IDs
- separate navigation presentation from workspace hosting
- add a left-navigation component backed by the same registry
- keep tab behavior as a compatibility implementation until the new shell passes navigation and packaging tests

## Workspace composition

### `ui/viewport_fit_feature.py`

**Classification:** `MIGRATE`

**Strengths**

- preserves current Inventory, Pricing, and Listings separation
- adds scrolling and viewport fit
- creates explicit cross-workspace handoffs

**Debt**

- hard-coded light colors and spacing
- inline title/subtitle styles
- direct mutation and movement of widgets between layouts
- method wrapping to react to selection
- compatibility attributes published onto the main window
- workspace construction and cross-workspace behavior are concentrated in one feature

**Migration direction**

- move each workspace into a dedicated module
- replace handoff `QGroupBox` with reusable guidance/recommendation components
- replace wrapped methods with typed selection/context events
- consume spacing, typography, and surface tokens
- preserve current cross-workspace flow and stable IDs during migration

## Theme surfaces

### `app/ui/themes/theme.qss`

**Classification:** `REVIEW / MIGRATE / RETIRE`

- contains a small independent dark theme
- uses hard-coded colors and control styling
- exists in the legacy `app/` tree rather than the authoritative root UI

Unique useful values may inform migration, but this file must not become a second theme authority.

### `app/ui/themes/theme_manager.py`

**Classification:** `REVIEW / RETIRE`

- defines another independent dark stylesheet
- conflicts with the one-design-system rule
- contains global label sizing that would make data-heavy screens inconsistent

Retirement requires reference search and proof that no production path depends on it.

### Inline styles in root UI and feature modules

**Classification:** `MIGRATE`

Known examples include:

- root title and KPI values
- compact Inventory values
- workspace handoff cards
- Pricing title/subtitle
- Listing preparation/readiness panels
- marketplace package and execution panels

Every hard-coded visual value should be classified and replaced only when its component migrates.

## Existing reusable component evidence

### `app/ui/widgets/md_dashboard_card.py`

**Classification:** `REVIEW / ADAPT`

This is a minimal `QFrame` with title and value labels. It proves prior intent for a shared dashboard card but lacks:

- semantic tokens
- evidence state
- comparison period
- trend
- loading/empty/error states
- accessibility contract
- drill-down behavior

Do not promote it directly into root authority. Reuse only proven ideas through the new `kpi-card` contract.

## Legacy Mission Control surfaces

### `app/ui/pages/mission_control.py`

**Classification:** `REVIEW / MIGRATE / RETIRE`

- uses static placeholder values
- is not wired to the canonical root Mission Control service
- provides basic card and quick-action layout ideas

It must not become production authority or supply mock values to the real application. Unique layout ideas may be translated into reusable components after comparison.

### Duplicate nested `app/ui/pages/pages/mission_control.py`

**Classification:** `REVIEW / RETIRE`

The duplicate path suggests legacy tree drift. Confirm references and unique behavior before removal.

## Feature-module presentation

### Inventory, Pricing, Listings, and sale-completion feature files

**Classification:** `KEEP behavior / MIGRATE presentation`

The files contain mature workflow behavior and focused tests, but many build `QGroupBox`, labels, buttons, and styles independently.

Migration rule:

- do not rebuild calculations, readiness, publication, sale, or settlement behavior
- wrap existing read models/actions with shared components
- migrate visual surfaces one coherent workflow section at a time
- preserve exact confirmations, blockers, and evidence semantics

## Dialogs and forms

**Classification:** `KEEP behavior / MIGRATE presentation`

Current dialogs are functional but visually default and embedded in the root main window.

Target shared patterns:

- form field
- labeled input
- validation message
- money input
- quantity input
- date input
- primary/secondary action row
- destructive confirmation
- error recovery

Form migration may not change validation, persistence, or confirmation boundaries.

## Tables

**Classification:** `KEEP data behavior / MIGRATE component`

The current Inventory table provides authoritative row selection, sorting, filtering, and multi-select behavior.

Target `data-table` component must preserve:

- stable row identity
- selection model
- sort and filter behavior
- archived/active distinction
- accessible headers
- keyboard navigation
- evidence/detail access
- large dataset performance

Visual changes must not move authority into the widget.

## Accessibility audit

### Existing positive evidence

- workspace host has an accessible name
- standard Qt controls provide baseline keyboard behavior
- destructive actions use confirmation dialogs
- text labels accompany many statuses

### Gaps

- many controls rely on visible text only and have no explicit accessible context
- emoji icons may not have useful accessible descriptions
- focus appearance is not centrally controlled
- color contrast is not centrally tested
- no reduced-motion or large-text path
- no chart text alternative because reusable charts do not yet exist
- no common window-size or high-DPI evidence

## Brand and asset audit

### Present

- historical Visual North Star root asset
- canonical mascot root asset
- brand manifest and identity tests
- approved v1 identity metadata

### Pending

- v1 PNG at canonical organized path
- production asset resolver
- source/package/installer/installed-runtime resolution
- header mascot implementation
- About/empty/loading/success/assistant artwork
- visual baseline screenshots

## Gamification audit

No authoritative trainer level, XP, badge, quest, or achievement domain exists yet.

**Classification:** `NEW FUTURE CAPABILITY / FOUNDATION ONLY`

The current visual foundation may include component contracts and reserved layout zones, but production gamification must wait for:

- activity definitions
- authoritative event sources
- scoring rules
- opt-out/settings
- audit and correction behavior
- anti-pressure and data-quality rules

## First production migration slice

### Recommended scope

**Mission Control Header + KPI Card Foundation**

Build:

1. PySide theme adapter from `MarketDEXDesignTokens`
2. branded workspace header with compact mascot placement
3. reusable KPI card
4. status badge
5. dashboard panel container
6. loading, empty, and error state components

Apply them to the existing canonical Mission Control snapshot without adding metrics or changing service keys.

### Why this slice

- highest visual impact
- reuses current authoritative read model
- proves tokens and components with real data
- does not require schema changes
- establishes shell/header direction
- provides reusable components for Inventory, Collection, Market Compass, and Reports
- creates an early visual acceptance surface

### Protected behavior

- exact Mission Control snapshot semantics
- root launcher and MainWindow authority
- Inventory actions and table behavior
- database path and read-only projection rules
- existing workspace IDs and navigation
- package and installer entry paths

## Second migration slice

**Inventory Workspace Header + Summary + Table Chrome**

After the first slice passes:

- replace summary `QGroupBox` widgets with KPI cards
- apply filter bar and data-table component styling
- introduce branded empty/loading/error states
- preserve all Inventory command and selection behavior

## Classification summary

| Surface | Classification | Next action |
|---|---|---|
| root `MainWindow` | KEEP / ADAPT | Split presentation responsibilities incrementally |
| `WorkspaceHost` | KEEP / ADAPT | Preserve registry behavior; migrate visual navigation |
| `viewport_fit_feature` | MIGRATE | Move to workspace modules and typed context events |
| root business feature modules | KEEP behavior / MIGRATE presentation | Compose shared components around existing logic |
| `app/ui/themes/*` | REVIEW / RETIRE | Prevent competing theme authority |
| `app/ui/widgets/md_dashboard_card.py` | REVIEW / ADAPT | Translate useful intent into canonical KPI card |
| legacy Mission Control pages | REVIEW / RETIRE | Never promote static mock values |
| root dialogs/forms | KEEP behavior / MIGRATE presentation | Extract shared form components |
| root tables | KEEP behavior / MIGRATE component | Preserve authority and keyboard model |
| gamification | NEW FUTURE CAPABILITY | Define authoritative activity model before production |

## Gate result

- Authority: PASS FOR AUDIT
- Architecture: PASS FOR AUDIT
- Visual Identity: PASS FOR DIRECTION
- Design System: READY FOR FIRST PYSide IMPLEMENTATION
- Behavior: NOT CHANGED
- Data: NOT CHANGED
- Accessibility: GAPS RECORDED
- Packaging: PENDING
- Release: BLOCKED by existing stack and visual implementation requirements

## Exact next implementation step

Create a PySide6 token/theme adapter and the first reusable `MarketDEXKpiCard`, `MarketDEXWorkspaceHeader`, `MarketDEXStatusBadge`, and `MarketDEXDashboardPanel` components. Apply them only to a real Mission Control slice while preserving the existing snapshot contract and tests.