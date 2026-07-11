# EC-008 — Gamified Visual North Star and Design-System Foundation

**Checkpoint date:** 2026-07-11  
**Status:** Visual direction and reusable contracts established; binary asset synchronization and production UI adoption remain pending  
**Branch:** `agent/market-intelligence-foundation`  
**Pull request:** Draft PR #166  
**Head at checkpoint creation:** `9828bea3c1581c36be2dbcef4c1ba7d11dd47f4d`

## Product Owner decision

The Product Owner formally approved the gamified MarketDEX dashboard concept as the active Visual North Star and long-term quality benchmark for the application shell, navigation, dashboards, workspaces, information hierarchy, component language, charts, branding, interaction states, optional progress systems, and overall user experience.

This direction supersedes the earlier Mission Control concept as the active destination without deleting the earlier image from historical repository evidence.

The Product Owner also reaffirmed that the original gray-and-white electric dog Pokémon mascot is permanent and may never be replaced, removed, substantially redesigned, recolored, restyled, or silently substituted.

## Active Visual North Star identity

Intended canonical path:

`assets/brand/visual_north_star/marketdex_visual_north_star_v1.png`

Approved identity:

- Dimensions: `1536 × 1024`
- File size: `2,863,520 bytes`
- SHA-256: `1269e2af119c569cc5d4f76b82a6f92984a04f6f752119d8e1dcf417557909a5`
- Git blob SHA when committed unchanged: `27d4b34b24984678225ae38c7e77240a02d521b4`

Historical predecessor retained:

`MarketDEX_Mission_Control_Visual_North_Star.png`

The predecessor remains historical evidence and must not silently regain active design authority.

## Mascot identity

Current canonical source:

`MarketDEX_Official_Mascot.png`

Approved identity:

- Dimensions: `1254 × 1254`
- File size: `2,269,552 bytes`
- SHA-256: `32fad644bd5e8f6cfa4a3166913030fc4520ad0fef560943f4e432a5f39cebc4`
- Git blob SHA: `5c192e8833896cf754f20fcb636d30098bc75ecf`

The approved dashboard keeps mascot use compact: a recognizable brand treatment near the MarketDEX wordmark and selected assistant, onboarding, empty, loading, success, About, installer, and release moments. Business information remains the visual priority.

## Approved experience direction

MarketDEX should feel like a cohesive Pokémon TCG business and collecting operating system rather than a spreadsheet replacement, generic database, or unrelated desktop forms.

It should communicate:

- intelligence
- confidence
- organization
- speed
- professionalism
- collector personality
- business readiness
- clear decision support
- premium desktop quality
- recognizable MarketDEX identity

Permanent comprehension rules:

- `Enter once. Understand everywhere.`
- `Decisions first. Evidence second. Raw metrics on demand.`
- `Scan → Recognize → Understand → Investigate.`

## Approved visual language

- deep navy and dark-blue structure
- bright blue, cyan, gold, red, green, and purple semantic accents
- controlled glow and depth
- crisp panel borders
- rounded professional geometry
- prominent readable values
- dense but understandable information hierarchy
- meaningful icons and state feedback
- non-color-only communication

## Approved shell and workspace direction

The stable shell should eventually provide:

- branded top header
- persistent left navigation
- reporting period and business date
- data freshness, database, backup, import, offline, and health status
- global search or command access
- Business / Collector mode
- notifications and Needs Attention
- assistant access
- central registered workspaces

Mission Control is the first production-quality reference workspace. It should prove that real MarketDEX data, shared components, responsiveness, explainability, navigation, and professional mascot integration can meet the Visual North Star.

## Approved panel and chart concepts

- KPI cards
- portfolio and value trends
- inventory and collection composition
- market sentiment
- daily sales volume
- opportunities and risks
- sealed-versus-open analysis
- price-per-pack calculation
- marketplace performance
- listing performance
- Collector Pulse
- heat maps
- sparklines
- supporting evidence tables

Every chart or panel must define its business question, authority owner, data source, freshness, confidence, loading/empty/error states, accessible explanation, and drill-down destination.

## Business Mode and Collector Mode

Modes are presentation lenses over shared authority.

Business Mode emphasizes profit, ROI, turnover, listing readiness, sales, expenses, fees, cash deployment, fulfillment, settlement, and operational attention.

Collector Mode emphasizes collection completion, set progress, personal value, grading goals, discovery, trade planning, wishlist progress, and keep/watch/trade/sell/open/keep-sealed analysis.

## Gamification approval

Approved future visual and capability concepts:

- trainer level
- experience progress
- badges
- daily quests or objectives
- achievements
- collection and business milestones
- optional assistant encouragement

Gamification remains optional, evidence-based, respectful, and subordinate to operational information. It may not pressure purchases or sales, reward incomplete data, or hide financial and risk information.

## New permanent authorities

### Visual direction

`docs/design/VISUAL_NORTH_STAR.md`

This is the active detailed design and phased-implementation authority.

### Design-system foundation

`docs/design/DESIGN_SYSTEM_FOUNDATION.md`

Defines semantic tokens, component contracts, accessibility, chart behavior, gamification limits, mascot rules, and migration strategy.

### Semantic token implementation

`ui/design_system/tokens.py`

Defines versioned color, typography, spacing, density, shape, elevation, icon, and motion roles without importing PySide6 or business infrastructure.

### Component contracts

`ui/design_system/component_contracts.py`

Defines stable reusable contracts for the shell, navigation, headers, KPI cards, panels, tables, charts, attention, recommendations, states, assistant, mascot guidance, and progress components.

### Asset directory authority

- `assets/brand/visual_north_star/README.md`
- `assets/brand/mascot/README.md`

These preserve expected canonical paths and exact approved identities.

### Permanent tests

`tests/test_design_system_foundation.py`

Protects the Visual North Star identity metadata, design-system completeness, component IDs, PySide independence, accessibility requirements, and brand directory identity records.

## Gate status

| Gate | Result | Evidence |
|---|---|---|
| Vision Continuity | PASS | Product Owner direction preserved in permanent design and checkpoint files |
| Authority | PASS FOR PLANNING | Active v1 direction and historical predecessor are explicitly separated |
| Visual Identity | PASS FOR DIRECTION | Exact approved v1 identity and mascot identity documented |
| Design System | PASS FOR FOUNDATION | Semantic token and component contracts implemented and tested |
| Architecture | PASS FOR FOUNDATION | UI foundation remains presentation-safe and does not alter business authority |
| Terminology | PASS | Existing canonical workspace names preserved |
| UX and Accessibility | DESIGN PASS | Keyboard, focus, scaling, contrast, states, and non-color-only requirements documented |
| Gamification | FOUNDATION PASS | Optional, meaningful, non-disruptive rules documented |
| Behavior | NOT CHANGED | No production workflow behavior changed |
| Data | NOT CHANGED | No schema or persisted identifier changed |
| Active v1 Binary Asset | PENDING | Exact local source is approved, but the PNG still requires repository binary synchronization at the canonical path |
| Packaging | BLOCKED | Active v1 asset and production asset resolver are not yet integrated into executable/installer verification |
| Release | BLOCKED | Draft stack, Listing gate, binary synchronization, and production visual adoption remain incomplete |

## Known limitations

- The active v1 PNG is not yet committed at its canonical repository path.
- Existing production UI has not been audited against the component system.
- The token set is an initial controlled approximation and has not received rendered PySide visual acceptance.
- Concrete PySide6 components do not yet implement the contracts.
- Mission Control has not yet been migrated to the new design system.
- Packaged runtime and installer do not yet resolve the active v1 asset through the brand manifest.
- High-DPI, practical window size, reduced motion, and screenshot regression checks are not yet implemented.
- The known Listing CI failure remains deferred and still blocks stack readiness.

## Exact resume point

1. Synchronize the approved v1 PNG to `assets/brand/visual_north_star/marketdex_visual_north_star_v1.png` and verify the expected SHA-256 and Git blob identities.
2. Promote the v1 file into `branding/asset_manifest.py` and required brand-asset tests while retaining the prior image as historical evidence.
3. Perform the Current UI and Component Audit using `KEEP`, `ADAPT`, `MIGRATE`, `RETIRE`, and `REVIEW` classifications.
4. Build a PySide6 theme adapter over the semantic tokens.
5. Implement the first reusable production components: navigation item, workspace header, KPI card, dashboard panel, status badge, chart container, and empty/loading/error states.
6. Apply those components to one real Mission Control section without changing its authoritative read model.
7. Continue the canonical domain, ownership, persistence, and migration architecture in parallel.
8. Return to the Listing CI failure before any stacked PR is marked ready or merged.
9. Run all architecture, behavior, design-system, accessibility, packaging, installed-runtime, and release gates on final heads.

## Non-negotiable continuity rule

Future contributors and AI assistants must read `MARKETDEX_START_HERE.md`, `docs/design/VISUAL_NORTH_STAR.md`, this checkpoint, and the latest `FoundationCheckpoint.md` before changing MarketDEX UI, branding, gamification, mascot usage, packaging, installer artwork, or product identity.

A polished static image is not completion. Completion requires real data, reusable components, preserved workflows, accessibility, performance, packaging, and green gates.