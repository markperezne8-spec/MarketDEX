# MarketDEX Design System Foundation

**Status:** Foundation contract  
**Authority:** `docs/design/VISUAL_NORTH_STAR.md`  
**Initial implementation:** `ui/design_system/`

## Purpose

The MarketDEX design system turns the approved Visual North Star into reusable, testable implementation rules. It prevents each workspace from inventing independent colors, spacing, states, tables, charts, and interaction patterns.

The foundation is intentionally presentation-safe and incremental. It does not replace business services, repositories, or workflows.

## Architecture

```text
Visual North Star and Product Principles
                 ↓
Semantic Design Tokens
                 ↓
Reusable Component Contracts
                 ↓
PySide6 Component Implementations
                 ↓
Workspace Composition
                 ↓
Visual Regression and Release Gates
```

Tokens and component contracts must not import business repositories or mutate authoritative data.

## Token families

### Color

Colors are semantic roles rather than page-specific constants:

- application and shell backgrounds
- primary, secondary, elevated, and interactive surfaces
- subtle and strong borders
- primary, secondary, and muted text
- primary action and hover
- information
- positive
- warning
- negative
- opportunity
- collection
- research
- focus
- disabled
- reusable chart series

The same meaning should use the same role throughout MarketDEX.

### Typography

The initial scale defines:

- display
- workspace title
- section title
- card title
- KPI value
- body
- strong body
- caption
- label
- monospace numeric value

Typography choices must prioritize readability, alignment, numerical scanning, and high-DPI behavior.

### Spacing and density

Spacing uses a controlled scale. Four density modes are defined:

- compact
- standard
- comfortable
- large text

The initial desktop default should be standard. Data-heavy tables may use compact density when readability remains acceptable. Large-text density is an accessibility path, not a different product theme.

### Shape, depth, and motion

The foundation defines:

- corner radii
- border widths
- elevation levels
- icon sizes
- motion durations

Motion must remain brief, meaningful, and optional under reduced-motion preferences.

## Component contract

Each reusable component records:

- stable component ID
- user-facing name
- purpose
- required states
- keyboard requirement
- accessibility requirement
- authoritative data requirement
- mascot policy

Concrete PySide6 implementations must satisfy these contracts instead of redefining them.

## Initial component catalog

The first catalog includes:

- Application Shell
- Navigation Item
- Workspace Header
- KPI Card
- Dashboard Panel
- Status Badge
- Needs Attention Row
- Opportunity Card
- Recommendation Card
- Chart Container
- Data Table
- Filter Bar
- Search Control
- Segmented Control
- Primary Button
- Secondary Button
- Business / Collector Mode Selector
- Empty State
- Loading State
- Error State
- Confirmation Dialog
- Detail Drawer
- Mascot Guidance Panel
- Assistant Launcher
- Progress / Achievement Card

## Required states

Components declare relevant states from:

- default
- hover
- pressed
- focused
- selected
- disabled
- loading
- empty
- success
- warning
- error
- insufficient data

Missing states may not silently fall back to unreadable or misleading presentation.

## Chart contract

A chart implementation must receive a serializable read model containing:

- metric identity
- business question
- series and units
- start/end dates
- selected comparison period
- source coverage
- freshness
- confidence or evidence state
- supporting text/table data
- drill-down target

Widgets must not query arbitrary tables directly.

## Gamification contract

Progress and achievement components are visual foundations only until the underlying activity model is approved and authoritative.

Gamification must:

- be optional
- reward accurate and meaningful actions
- expose the activity basis
- avoid pressure to buy, sell, list, or transact unnecessarily
- never hide financial or risk information
- remain visually subordinate to primary operational content

## Mascot contract

The mascot may appear through controlled components such as product branding, guidance, empty/loading/success states, and assistant access.

Only the canonical asset may be used. Components must not crop destructively, recolor, restyle, or substitute it. Routine business panels should not display mascot artwork.

## Accessibility gate

Each implemented component must verify:

- keyboard reachability
- visible focus
- sufficient contrast
- non-color-only meaning
- scalable labels and values
- high-DPI rendering
- useful accessible names
- reasonable control size
- reduced-motion behavior where applicable
- empty/loading/error announcements

## Migration strategy

1. Audit existing styles and widgets.
2. Map existing controls to component contracts.
3. Introduce token access without changing behavior.
4. Implement components one family at a time.
5. Adopt components in Mission Control first.
6. Preserve routes, services, repositories, and tests.
7. Add visual review and regression baselines.
8. Migrate additional workspaces gradually.
9. Retire old one-off styling only after reference and compatibility evidence.

## Initial completion boundary

This foundation is not complete because token and component contracts exist. The first implementation milestone requires:

- current UI audit
- central theme/token adapter for PySide6
- first reusable production components
- at least one real Mission Control section using them
- high-DPI and resizing checks
- packaged asset resolution
- screenshot or human visual acceptance
- green applicable gates
