# MarketDEX — Start Here

**Status:** Permanent project orientation and continuity index  
**Purpose:** Ensure future contributors, AI assistants, and development sessions continue from repository authority instead of restarting from chat memory.

## Product north star

> **Enter once. Understand everywhere.**

> **Decisions first. Evidence second. Raw metrics on demand.**

MarketDEX is a desktop-first, offline-first collectibles business operating system. Pokémon TCG is the first optimized workflow. The architecture must remain extensible to other TCGs, sealed gaming products, graded collectibles, Funko Pops, gaming collectibles, and related products.

The current goal is to build the best possible Windows desktop experience for people and authorized AI assistants. iOS, Android, and browser clients remain future compatibility targets only.

## Non-negotiable identity

The following are permanent MarketDEX product requirements:

- `MarketDEX_Mission_Control_Visual_North_Star.png`
- `MarketDEX_Official_Mascot.png`
- `docs/governance/Visual_North_Star_and_Mascot_Standard.md`
- `branding/asset_manifest.py`

The Visual North Star is the central visual ambition for MarketDEX. The approved electric dog mascot is a permanent brand element and may not be replaced, substantially redesigned, silently omitted, or substituted without explicit Product Owner approval and a checkpoint update.

## Read in this order

Every new MarketDEX work session should begin with:

1. `FoundationCheckpoint.md` — current state, active gates, and exact resume point
2. `docs/governance/Product_Vision_Idea_Register.md` — approved product ideas and future possibilities
3. `docs/governance/Visual_North_Star_and_Mascot_Standard.md` — permanent visual identity and asset rules
4. `docs/governance/Canonical_Product_Terminology.md` — canonical user-facing names and compatibility aliases
5. `docs/Architecture/Modular_Collectibles_Platform_Blueprint.md` — target architecture
6. `docs/Architecture/Current_to_Target_Module_Map.md` — what to keep, adapt, migrate, retire, or review
7. `docs/governance/Approved_Architecture_Roadmap.md` — approved implementation sequence
8. `docs/governance/Architecture_Gates.md` — mandatory pass/fail requirements
9. latest file in `docs/checkpoints/` — detailed in-progress evidence
10. current pull request and GitHub Actions state

## Source-of-truth order

1. Merged `main` implementation
2. Accepted business specifications and workbook evidence
3. Permanent tests and GitHub Actions
4. `FoundationCheckpoint.md`
5. `CheckpointManifest.md`
6. Approved governance and architecture documents
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
- Stable identities independent from widget order
- Typed commands, queries, events, and read models
- Replaceable repository and provider adapters
- No direct AI or external-adapter mutation of canonical SQLite authority
- No mobile or web application tree during the desktop-first phase
- No destructive migration without backup, validation, historical fixtures, and rollback planning
- No recommendation without evidence, freshness, confidence, and explanation
- No chart without a business question and metric owner
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
- architecture, terminology, platform, AI, packaging, and release gates
- Visual North Star and mascot safeguards
- current-to-target module migration map

## Next foundation step

The next architecture package is the **Canonical Domain, Identity, and Ownership Model**.

It should define:

- Product
- Product Variant
- Collectible Category
- Game or Product Line
- Set or Release
- Product Type
- Product Form
- Condition
- Grade
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
- packaged executable and installer must contain required brand assets
- brand assets must match the canonical manifest
- the Visual North Star must remain the visual authority
- the mascot must remain present and correctly rendered
- `FoundationCheckpoint.md` and checkpoint evidence must be updated

## Core instruction

> Improve the existing MarketDEX foundation. Do not restart it, duplicate it, or silently redefine it.