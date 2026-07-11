# EC-006 — Vision Continuity, Modular Platform, and Canonical Naming

**Checkpoint date:** 2026-07-11  
**Status:** Architecture planning checkpoint complete; implementation stack remains draft  
**Authority:** Product Owner approval, repository foundation documents, draft PR heads, and permanent governance tests

## Product Owner approval

The Product Owner approved all available prior MarketDEX architecture and product recommendations that do not conflict with a newer explicit decision or established source-of-truth rule.

This approval includes continued recommendation generation and controlled architecture planning. It does not authorize destructive data changes, credential use, paid services, publishing, spending, or pull-request merges without the applicable authority and gates.

## Permanent product direction

- Build the best Windows desktop collectibles operating system first.
- Make Pokémon TCG selling and collection operation effortless.
- Preserve extensibility for other TCGs, sealed gaming products, graded collectibles, Funko Pops, gaming collectibles, and related products.
- Keep iOS, Android, and browser clients as future compatibility plans only.
- Keep the visible experience simple even when the underlying system is feature-rich.
- Support people and authorized AI assistants through the same controlled application contracts.
- Never restart from chat memory; continue from repository-backed vision, architecture, history, and checkpoints.

## Sources reconciled

The checkpoint reviewed and preserved direction from:

- `Vision.md`
- `WorkbookBlueprint.md`
- `FoundationCheckpoint.md`
- `docs/governance/Approved_Architecture_Roadmap.md`
- `docs/governance/Platform_Strategy.md`
- `docs/governance/Architecture_Gates.md`
- `docs/checkpoints/EC-005_Shell_Composition_Market_Intelligence.md`
- the current MarketDEX architecture and product discussions

## New permanent authorities

### Product vision and idea register

`docs/governance/Product_Vision_Idea_Register.md`

Preserves:

- product north star and operating principles
- desktop-first and future-platform direction
- supported and future collectible categories
- complete seller and collector workflows
- market intelligence, marketplace, Google Trends, volume, sentiment, heat map, and chart ideas
- Business and Collector modes
- keep/sell/trade/grade/open/break/keep-sealed decisions
- AI assistance boundaries
- upgradability, jobs, backups, diagnostics, imports, and future possibilities
- idea status and continuity rules

### Canonical terminology

`docs/governance/Canonical_Product_Terminology.md`

Resolves overlapping names and preserves controlled migration rules.

### Modular platform blueprint

`docs/Architecture/Modular_Collectibles_Platform_Blueprint.md`

Defines:

- presentation/application/domain/infrastructure separation
- module contracts and extension packs
- catalog, ownership, commercial, and market authority boundaries
- commands, queries, events, read models, adapters, and AI tools
- persistence, migration, identity, settings, jobs, diagnostics, and future-client readiness
- recommended implementation order

## Naming conflicts resolved

| Conflicting or overloaded term | Canonical direction |
|---|---|
| Dashboard / Home Dashboard | Mission Control |
| Platform for eBay/TCGplayer | Marketplace; Platform is reserved for Windows/iOS/Android/web |
| Asset Manager | Inventory or Collection based on ownership intent |
| Business module | Business Operations; Business Mode remains the presentation lens |
| Analytics workspace | Reports & Insights |
| Alerts / Attention Center | Needs Attention; Task Center is separate operational work |
| Listing Workflow | Listings as long-term user-facing name; stable legacy ID retained until gated migration |
| Personal Collection | Collection |
| Marketplace Dashboard / Platform Analysis | Market Compass |
| Market Pulse | Collector Pulse |

These naming decisions do not authorize immediate persisted-ID or API renames. Compatibility aliases and migrations remain mandatory.

## Expanded mandatory gate stack

1. Vision Continuity
2. Authority
3. Architecture
4. Terminology Compatibility
5. Behavior
6. Data and Migration
7. UX and Accessibility
8. Integration and Provenance
9. Platform Compatibility
10. AI Safety
11. Packaging and Installed Runtime
12. Release and Checkpoint

## Checkpoint results

| Gate | Result | Evidence |
|---|---|---|
| Vision Continuity | PASS | Approved ideas consolidated in a living repository register |
| Authority | PASS FOR PLANNING | Existing source-of-truth hierarchy preserved; draft PRs remain proposals |
| Architecture | PASS FOR PLANNING | Modular platform blueprint defines target boundaries and extension model |
| Terminology Compatibility | PASS FOR NEW WORK | Canonical dictionary and controlled legacy-alias rule established |
| Behavior | NOT CHANGED | No business behavior changed in this checkpoint |
| Data | NOT CHANGED | No schema, migration, or persisted identifier changed |
| UX | DESIGN PASS | Canonical names and progressive-disclosure principles documented |
| Integration | DESIGN PASS | Adapter and provenance boundaries preserved |
| Platform Compatibility | DESIGN PASS | Desktop-first, future-client-compatible separation preserved |
| AI Safety | DESIGN PASS | AI remains a controlled application client, never direct database authority |
| Packaging | NOT CHANGED | No packaging code changed; prior successful desktop build evidence remains separate |
| Release | BLOCKED | PRs #164–#166 remain draft; Listing CI failure remains unresolved by explicit deferral |

## Current known implementation status

- PR #163 is merged.
- PRs #164, #165, and #166 remain stacked drafts.
- Core, Inventory, Pricing, governance, Windows build, packaged runtime, installer, and installed runtime gates passed on the latest observed run.
- The Listing gate remains failing and must be repaired before merge.
- The Product Owner explicitly directed architecture planning and vision preservation to continue before returning to that fix.

## Exact resume point

1. Continue canonical domain and data architecture planning from the modular blueprint.
2. Produce a current-code-to-target-module map with `KEEP`, `ADAPT`, `MIGRATE`, `RETIRE`, and `REVIEW` classifications.
3. Design the canonical persistence and migration authority, including historical upgrade fixtures and rollback.
4. Define first-version command, query, event, and read-model contracts for Inventory, Collection, Listings, Market Data, and Attention.
5. Preserve each new product or architecture idea in the idea register and checkpoint history.
6. Return to the Listing CI failure before any stacked PR is marked ready or merged.
7. Re-run all mandatory gates on final heads and reconcile the stack in dependency order.

## Continuity rule

Future MarketDEX work should begin by reading, in order:

1. `FoundationCheckpoint.md`
2. `docs/governance/Product_Vision_Idea_Register.md`
3. `docs/governance/Canonical_Product_Terminology.md`
4. `docs/Architecture/Modular_Collectibles_Platform_Blueprint.md`
5. `docs/governance/Approved_Architecture_Roadmap.md`
6. the latest EC checkpoint
7. current PR and CI state

This sequence preserves the vision, prevents rediscovery, and supplies the exact resume point.