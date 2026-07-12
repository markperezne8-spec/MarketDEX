# EC-010 — Vision Freeze and Foundation Baseline

**Checkpoint date:** 2026-07-11  
**Status:** Product vision frozen; foundation construction authorized  
**Branch:** `agent/market-intelligence-foundation`  
**Pull request:** Draft PR #166

## Product Owner decision

The MarketDEX idea-definition stage is complete enough to proceed into foundation construction.

The following are frozen unless the Product Owner explicitly approves a future change:

- the approved gamified Visual North Star as the long-term visual destination
- Windows desktop as the current delivery target
- offline-first operation and local authority
- Pokémon TCG as the first optimized workflow
- support for both serious business operations and personal collecting
- UI and UX quality as core product requirements
- the original gray-and-white electric dog Pokémon mascot as a permanent brand element
- one reusable design system and component architecture
- protection of existing business logic, user data, and stable workflows
- modular, testable, documented implementation through the permanent MarketDEX architecture
- phased modernization rather than one broad rewrite

Minor implementation refinement remains allowed. Colors, spacing, panel composition, and interaction details may improve through evidence and visual acceptance, but the identity, product philosophy, architecture principles, mascot requirement, and approved visual destination may not be silently redefined.

## Current repository baseline

- `main` remains delivered implementation authority.
- PR #163 is merged and establishes the workspace registry foundation.
- PR #164 remains the shell/workspace integration draft.
- PR #165 remains the canonical application-composition draft.
- PR #166 remains the vision, architecture, market-intelligence, design-system, UI-audit, and first-primitives draft.
- The required stack order remains `main → #164 → #165 → #166`.
- Draft work must not be described as delivered `main` capability.

## Existing foundation preserved

The active branch already contains:

- `MARKETDEX_START_HERE.md`
- the Product Vision and Idea Register
- canonical terminology
- modular platform and current-to-target architecture maps
- architecture gates
- the active Visual North Star standard
- mascot and brand governance
- the Current UI and Component Audit
- semantic design tokens
- reusable component contracts
- the Qt theme adapter
- the first reusable PySide widgets
- EC-005 through EC-009

These foundations must be continued and hardened rather than recreated through a competing architecture or prototype.

## Canonical visual asset gate

The exact approved v1 image must be synchronized to:

`assets/brand/visual_north_star/marketdex_visual_north_star_v1.png`

Required identity:

- Dimensions: `1536 × 1024`
- Size: `2,863,520 bytes`
- SHA-256: `1269e2af119c569cc5d4f76b82a6f92984a04f6f752119d8e1dcf417557909a5`
- Git blob SHA: `27d4b34b24984678225ae38c7e77240a02d521b4`

Issue #167 remains the explicit synchronization gate. The earlier root Visual North Star remains historical evidence and may not be removed by assumption.

## Permanent mascot authority

Canonical source:

`MarketDEX_Official_Mascot.png`

The mascot may not be replaced, removed, substantially redesigned, recolored, restyled, regenerated, or silently substituted.

## First approved construction task

**FDN-001 — Freeze Product Authority and Promote Canonical Visual Assets**

Controlled scope:

1. preserve this freeze decision in repository authority;
2. record the current branch, stack, runtime, schema, packaging, asset, and known-defect baseline;
3. synchronize the exact approved Visual North Star v1 binary;
4. promote v1 to required source and package authority;
5. preserve the historical visual and permanent mascot;
6. verify source, executable, installer, and installed-runtime asset resolution;
7. fail visibly when a required active asset is missing;
8. update checkpoint and PR evidence.

## Explicit exclusions

FDN-001 does not authorize:

- Mission Control redesign
- broad global theme adoption
- KPI, chart, metric, or read-model changes
- gamification behavior
- Business/Collector mode UI
- schema or migration changes
- operator-data mutation or reseeding
- Inventory, Pricing, Listings, sales, shipping, settlement, or audit behavior changes
- workspace-ID changes
- mascot changes
- removal of historical visual evidence
- a second launcher, shell, database authority, theme system, or prototype application
- merge or release classification

## Known blockers

- The exact approved v1 PNG is not yet present at its canonical path.
- The Listing CI failure remains unresolved and continues to block stack readiness.
- Production Mission Control adoption has not yet begun.
- Packaged and installed-runtime v1 asset verification remains pending.

## Required evidence for FDN-001 acceptance

- exact v1 dimensions, size, SHA-256, and Git blob identity
- historical visual preserved
- mascot identity unchanged
- active v1 and mascot required through the brand manifest
- visible failure for missing required assets
- source, executable, installer, and installed-runtime asset resolution
- no schema or migration change
- no operator-data mutation
- focused and applicable regression tests
- changed-file scope audit
- updated Foundation Checkpoint and PR evidence

## Exact resume point

1. Obtain the exact approved Visual North Star v1 PNG from the Product Owner.
2. Synchronize it through Issue #167 and verify every identity value.
3. Promote it to required source/package authority while retaining v0 as historical evidence.
4. Complete FDN-001 package, runtime, data-safety, and checkpoint evidence.
5. After Product Owner acceptance, begin FDN-002: apply the canonical token theme at one controlled root integration point and replace only the real Mission Control header and KPI presentation while preserving the exact snapshot and refresh behavior.
6. Repair the known Listing CI failure before any stacked PR is marked ready or merged.

## Core instruction

> Build against the frozen MarketDEX vision. Do not restart, duplicate, or silently redefine it.
