# MarketDEX — Start Here

**Status:** Permanent project orientation and continuity index  
**Purpose:** Ensure future contributors, AI assistants, and development sessions continue from repository authority instead of restarting from chat memory.

## Product north star

> **Enter once. Understand everywhere.**

> **Decisions first. Evidence second. Raw metrics on demand.**

> **Scan → Recognize → Understand → Investigate.**

MarketDEX is a desktop-first, offline-first collectibles business operating system. Pokémon TCG is the first optimized workflow. The architecture must remain extensible to other TCGs, sealed gaming products, graded collectibles, Funko Pops, gaming collectibles, and related products.

The current goal is to build the best possible Windows desktop experience for people and authorized AI assistants. iOS, Android, and browser clients remain future compatibility targets only.

## Non-negotiable visual and brand identity

The following are permanent MarketDEX product requirements:

- `docs/design/VISUAL_NORTH_STAR.md`
- `docs/design/DESIGN_SYSTEM_FOUNDATION.md`
- `assets/brand/visual_north_star/marketdex_visual_north_star_v1.png`
- `MarketDEX_Official_Mascot.png`
- `docs/governance/Visual_North_Star_and_Mascot_Standard.md`
- `ui/design_system/tokens.py`
- `ui/design_system/component_contracts.py`
- `branding/asset_manifest.py`

The approved gamified dashboard concept is the active Visual North Star. It defines the long-term quality level for the shell, navigation, workspaces, dashboards, components, visual hierarchy, charts, interaction states, and optional engagement features.

The earlier root image `MarketDEX_Mission_Control_Visual_North_Star.png` remains historical evidence. It may not override the active v1 direction.

The approved electric dog Pokémon mascot is a permanent brand element and may not be replaced, substantially redesigned, silently omitted, or substituted without explicit Product Owner approval and a checkpoint update. Mascot use should be compact and intentional so the business dashboard remains primary.

## Read in this order

Every new MarketDEX work session should begin with:

1. `FoundationCheckpoint.md` — current state, active gates, and exact resume point
2. `MARKETDEX_START_HERE.md` — permanent orientation
3. `docs/governance/Product_Vision_Idea_Register.md` — approved product ideas and future possibilities
4. `docs/design/VISUAL_NORTH_STAR.md` — active visual destination and phased implementation
5. `docs/design/DESIGN_SYSTEM_FOUNDATION.md` — semantic tokens and reusable component rules
6. `docs/governance/Visual_North_Star_and_Mascot_Standard.md` — permanent brand and asset rules
7. `docs/governance/Canonical_Product_Terminology.md` — canonical user-facing names and compatibility aliases
8. `docs/Architecture/Modular_Collectibles_Platform_Blueprint.md` — target architecture
9. `docs/Architecture/Current_to_Target_Module_Map.md` — what to keep, adapt, migrate, retire, or review
10. `docs/governance/Approved_Architecture_Roadmap.md` — approved implementation sequence
11. `docs/governance/Architecture_Gates.md` — mandatory pass/fail requirements
12. latest file in `docs/checkpoints/` — detailed in-progress evidence
13. current pull request and GitHub Actions state

## Source-of-truth order

1. Merged `main` implementation
2. Accepted business specifications and workbook evidence
3. Permanent tests and GitHub Actions
4. `FoundationCheckpoint.md`
5. `CheckpointManifest.md`
6. Approved design, governance, and architecture documents
7. EC checkpoint evidence
8. Draft pull requests as proposed work only
9. Chat summaries as navigation aids only

No chat-only statement is permanent product authority.

## Permanent architecture rules

- One launcher
- One desktop shell
- One application composition root
- One workspace registry
- One feature/module catalog
- One persistence, schema, and migration authority
- One semantic design-token authority
- One reusable component language
- Stable identities independent from widget order
- Typed commands, queries, events, and read models
- Replaceable repository and provider adapters
- No direct AI or external-adapter mutation of canonical SQLite authority
- No mobile or web application tree during the desktop-first phase
- No destructive migration without backup, validation, historical fixtures, and rollback planning
- No recommendation without evidence, freshness, confidence, and explanation
- No chart without a business question and metric owner
- No one-off page theme that bypasses the shared design system
- No release without all applicable gates and checkpoint evidence

## Canonical product vocabulary

Primary user-facing workspaces:

- Mission Control
- Inventory
- Collection
- Pricing
- Listings
- Orders & Shipping
- Sales & Settlement
- Market Compass
- Collector Pulse
- Research Lab
- Portfolio
- Reports & Insights
- Settings

Do not create competing names such as Dashboard, Asset Manager, Platform Analysis, Personal Collection, or Alerts Center without following the terminology compatibility process.

## Idea continuity rule

Every material new idea must be classified in `docs/governance/Product_Vision_Idea_Register.md` as:

- APPROVED — CURRENT
- APPROVED — FOUNDATION
- APPROVED — FUTURE
- RESEARCH
- REJECTED/SUPERSEDED

A newer decision may supersede an older one, but the replacement and reason must remain discoverable.

## Current building blocks

The active foundation includes:

- canonical shell and workspace architecture
- application composition root
- dependency-safe feature catalog
- Business and Collector modes
- marketplace and normalized market-observation contracts
- explainable attention signals
- chart and visualization catalog
- sealed-versus-open analysis
- Google Trends-compatible search-interest boundary
- architecture, terminology, platform, AI, packaging, design-system, visual-identity, and release gates
- active gamified Visual North Star direction
- permanent mascot safeguards
- semantic visual tokens
- reusable component contracts
- current-to-target module migration map

## Visual transformation rule

The Visual North Star is implemented incrementally:

1. preserve and checkpoint
2. audit current UI and styling
3. establish tokens and reusable components
4. upgrade the shell
5. build Mission Control as the first real reference workspace
6. migrate additional workspaces one at a time
7. add advanced animation, personalization, assistant moments, and gamification after foundations are proven

Do not attempt a massive visual rewrite or claim completion from a static mockup.

## Next foundation steps

### Immediate visual step

Complete the **Current UI and Component Audit**:

- map current shell, pages, styles, and assets
- locate duplicated colors, spacing, and widget patterns
- identify reusable existing widgets
- identify UI code coupled to business logic
- classify each surface as KEEP, ADAPT, MIGRATE, RETIRE, or REVIEW
- select the first real Mission Control components for token adoption

### Parallel domain step

Define the **Canonical Domain, Identity, and Ownership Model** covering:

- Product and Product Variant
- Collectible Category
- Game or Product Line
- Set or Release
- Product Type and Product Form
- Condition and Grade
- Lot
- Inventory Position
- Collection Position
- ownership intent and transitions
- stable identifiers
- lifecycle and history rules
- category-extension boundaries
- command, query, event, repository, and persistence requirements

After that, define the **Canonical Persistence and Migration Specification**.

## Release continuity

Draft architecture work remains proposed until merged. Before any release or merge sequence is considered complete:

- all required CI gates must pass
- the approved Visual North Star v1 asset must exist at its canonical path and match its identity
- packaged executable and installer must contain required brand assets
- the mascot must remain present and correctly rendered
- high-DPI and practical-window behavior must be tested
- at least one real workspace must use shared tokens and components
- `FoundationCheckpoint.md` and checkpoint evidence must be updated

## Core instruction

> Improve the existing MarketDEX foundation. Do not restart it, duplicate it, or silently redefine it.