# MarketDEX Foundation Checkpoint 058

**Status:** 🏗️ Active — Gamified Visual North Star, First UI Primitives, and Canonical Architecture Planning

## Active Phase

🖥️ **ACTIVE** — Build the best Windows desktop application for effortless collectible selling, collection intelligence, market awareness, and safe AI-assisted operation.

🎨 **DESIGN LOCKED** — The approved gamified dashboard is the active Visual North Star and long-term UI quality benchmark.

🐺 **PERMANENT BRAND** — The original gray-and-white electric dog Pokémon mascot remains the canonical MarketDEX mascot forever.

🧩 **FIRST PRIMITIVES COMPLETE** — Semantic tokens, component contracts, a PySide theme adapter, and the first reusable widgets now exist.

📱🌐 **FUTURE COMPATIBILITY ONLY** — iOS, Android, and web browser clients are future plans, not current implementation targets.

🧰 **FIXES DEFERRED BY PRODUCT OWNER FOR THIS STEP** — The known Listing CI failure remains real and blocking. Current work is focused on visual, architecture, and continuity foundations before returning to repair.

## Permanent Direction

> **Enter once. Understand everywhere.**

> **Decisions first. Evidence second. Raw metrics on demand.**

> **Scan → Recognize → Understand → Investigate.**

MarketDEX is an offline-first desktop operating system for collectors and sellers. Pokémon TCG is the first optimized workflow. The permanent architecture remains extensible to other TCGs, sealed gaming products, graded cards, Funko Pops, gaming collectibles, and related products.

## Active Visual North Star

### Approved v1 destination

- Intended canonical path: `assets/brand/visual_north_star/marketdex_visual_north_star_v1.png`
- Dimensions: `1536 × 1024`
- SHA-256: `1269e2af119c569cc5d4f76b82a6f92984a04f6f752119d8e1dcf417557909a5`
- Expected Git blob SHA: `27d4b34b24984678225ae38c7e77240a02d521b4`
- Binary synchronization gate: Issue #167

The prior root asset `MarketDEX_Mission_Control_Visual_North_Star.png` remains historical evidence but no longer controls the active visual destination.

### Canonical mascot

- Current source: `MarketDEX_Official_Mascot.png`
- Git blob SHA: `5c192e8833896cf754f20fcb636d30098bc75ecf`

The mascot may not be replaced, removed, significantly redesigned, recolored, restyled, or silently substituted. Approved use is compact and intentional so dashboards and business workflows remain primary.

## Approved Experience Direction

MarketDEX should feel like a polished, energetic, gamified Pokémon TCG business and collecting operating system—not a generic database or disconnected forms.

The interface combines:

- premium dark command-center structure
- clear KPI and attention hierarchy
- explainable opportunities and risks
- Business / Collector mode
- marketplace and market-intelligence visibility
- charts, volume, sentiment, and heat maps
- optional trainer levels, badges, quests, and achievements
- professional mascot integration
- accessibility, high-DPI behavior, performance, and offline reliability

Gamification remains optional, meaningful, evidence-based, and subordinate to financial and operational truth.

## Permanent Continuity Authorities

1. `main` and merged commits are implementation authority.
2. Accepted workbook artifacts are business-specification and traceability authority.
3. GitHub Actions and permanent tests are verification authority.
4. `FoundationCheckpoint.md` is current-state and exact-resume authority.
5. `CheckpointManifest.md` is completed historical checkpoint authority.
6. `MARKETDEX_START_HERE.md` is permanent orientation.
7. `docs/governance/Product_Vision_Idea_Register.md` is the living approved idea register.
8. `docs/design/VISUAL_NORTH_STAR.md` is the active visual-direction authority.
9. `docs/design/DESIGN_SYSTEM_FOUNDATION.md` is the reusable visual foundation authority.
10. `docs/design/CURRENT_UI_COMPONENT_AUDIT.md` is the current presentation migration baseline.
11. `docs/governance/Visual_North_Star_and_Mascot_Standard.md` is visual identity and mascot governance.
12. `ui/design_system/tokens.py` is semantic token authority.
13. `ui/design_system/component_contracts.py` is the component contract catalog.
14. `ui/design_system/qt_theme.py` is the PySide token adapter.
15. `ui/design_system/widgets.py` contains the first reusable PySide components.
16. `docs/governance/Canonical_Product_Terminology.md` is naming and compatibility authority.
17. `docs/Architecture/Modular_Collectibles_Platform_Blprint.md` is target modular architecture authority.
18. `docs/Architecture/Current_to_Target_Module_Map.md` maps current repository surfaces without deletion by assumption.
19. `docs/governance/Architecture_Gates.md` controls mandatory pass/fail requirements.
20. The latest EC checkpoint records detailed in-progress evidence.
21. Draft PRs remain proposals until merged and do not override `main`.

## Current Architecture Progress

- PR #163 merged: canonical workspace contract and registry foundation.
- PR #164 draft: professional `WorkspaceHost`, canonical workspace identities, and stable navigation.
- PR #165 draft: canonical `ApplicationComposition`, thin launcher, stable feature IDs, and dependency-safe installation.
- PR #166 draft: market intelligence, platform strategy, AI boundaries, vision continuity, naming, architecture, brand governance, active Visual North Star, semantic tokens, reusable component contracts, UI audit, PySide theme adapter, first reusable widgets, and checkpoints.
- EC-005 records shell/composition/market intelligence.
- EC-006 records vision continuity, modular architecture, naming, and repository mapping.
- EC-007 records the original Visual North Star and exact mascot lock.
- EC-008 records the approved gamified Visual North Star and design-system contracts.
- EC-009 records the Current UI Audit and first PySide primitives.

## Mandatory Gate Status

| Gate | Current status |
|---|---|
| Vision Continuity | PASS — approved direction is repository-backed |
| Authority | PASS FOR PLANNING — active v1 and historical predecessor are distinguished |
| Architecture | PASS FOR FOUNDATION — reusable UI components do not alter business authority |
| Terminology Compatibility | PASS — canonical workspace names preserved |
| Visual Identity | PASS FOR DIRECTION — exact v1 and mascot identities documented |
| Design System | PASS FOR FIRST PRIMITIVES — tokens, contracts, theme, and widgets exist |
| Current UI Audit | PASS — current/legacy surfaces are classified |
| Mascot Protection | PASS FOR FOUNDATION — canonical source and identity preserved |
| Gamification | FOUNDATION PASS — optional, meaningful, non-disruptive rules established |
| Behavior | BLOCKED FOR STACK — Listing test failure remains unresolved |
| Data and Migration | DESIGN PENDING — canonical persistence and migration authority remains required |
| UX and Accessibility | FOUNDATION PASS — focus, keyboard, scaling, contrast, and state rules established |
| Integration and Provenance | FOUNDATION PASS — replaceable adapters and evidence boundaries preserved |
| Platform Compatibility | FOUNDATION PASS — desktop-first with presentation-independent contracts |
| AI Safety | FOUNDATION PASS — controlled commands/read models; direct database mutation forbidden |
| Active v1 Binary Asset | PENDING — exact PNG must still be synchronized to its canonical path |
| Mission Control Adoption | NEXT — first real visual slice has not yet been integrated |
| Packaging | BLOCKED — v1 asset resolver and executable/installer inclusion are not yet implemented |
| Release | BLOCKED — draft stack, Listing failure, asset synchronization, and production visual adoption remain incomplete |

## Exact Resume Point

1. Synchronize the exact v1 PNG through issue #167 and verify its identity.
2. Promote v1 to required source and package authority while preserving v0 as historical evidence.
3. Apply `build_marketdex_qss()` at one controlled root UI integration point.
4. Replace only the existing Mission Control title and KPI `QGroupBox` surface with `MarketDEXWorkspaceHeader` and `MarketDEXKpiCard` while preserving every existing snapshot key and refresh behavior.
5. Add focused UI tests for value parity, accessibility, resizing, and interaction behavior.
6. Obtain visual acceptance at practical desktop resolutions.
7. Migrate Inventory summary cards and table chrome only after the Mission Control slice passes.
8. Define the canonical domain identity and ownership model.
9. Design one persistence, schema, and migration authority with backup, validation, restart, rollback, and historical fixtures.
10. Return to the Listing CI failure before marking any stacked PR ready or merging.
11. Re-run all architecture, behavior, accessibility, packaging, installed-runtime, and release gates on final heads.

## Progress

**Vision, visual direction, brand, and architecture planning:** `[██████████] 100%`  
**Design-system foundation:** `[██████████] 100%`  
**Production visual implementation:** `[██░░░░░░░░] 20%`  
**Stack validation and merge readiness:** `[█████████░] 92%`

## Core Operating Principle

> **Enter once. Understand everywhere.**