# MarketDEX Checkpoint 022 — Calc Build 036 Handoff

**Status:** 🏁 Continuity Checkpoint
**Date:** 2026-07-05

## Current State
- Build 033 — Listing Preparation Action is implemented, visually accepted, architecture-reviewed, and preserved.
- Build 034 — Condition Preparation Action is implemented, visually accepted, architecture-reviewed, and preserved.
- Build 035 — Listing Content Preparation Action is implemented, visually accepted, architecture-reviewed, and preserved.
- Official current Calc baseline: `artifacts/calc/MarketDEX_Calc_V0_Build035_Listing_Content_Preparation_Action.ods`

## Proven Preparation Chain
`Photos → Condition → Listing Content → Price Decision`

### Build 033
`PREPARE PRODUCT PHOTOS → COMPLETE · DEMO → PHOTOS CLEARED · DEMO → PREPARATION NEEDED → NEXT BLOCKER: CONDITION`

### Build 034
`REVIEW PRODUCT CONDITION → COMPLETE · DEMO → SEALED · ACCEPTABLE FOR LISTING · DEMO → CONDITION REVIEWED · DEMO → PREPARATION NEEDED → NEXT BLOCKER: LISTING CONTENT`

### Build 035
`PREPARE LISTING CONTENT → COMPLETE · DEMO → TITLE + BASIC DESCRIPTION PREPARED · DEMO → LISTING CONTENT PREPARED · DEMO → PREPARATION NEEDED → NEXT BLOCKER: PRICE DECISION`

## Locked Operating Principle
Preparation actions resolve one supported blocker at a time. Completing one task cannot silently make inventory READY TO LIST.

Each preparation action must:
- expose the current task,
- show task state,
- record minimum supporting evidence,
- identify the blocker affected,
- show the result after completion,
- reevaluate overall Listing Readiness,
- expose the next remaining blocker,
- preserve every unrelated blocker and authoritative inventory fact.

## Workflow Refinement
- Mark performs visual acceptance for visual workbook changes.
- Jarvis may implement routine design-locked Calc builds when the actual baseline ODS is available for safe package inspection.
- Use package/XML integrity verification plus visual architecture review as the smallest sufficient path for routine builds.
- Reserve Codex for high-risk native ODS work, difficult debugging, or milestone verification when specialist value materially helps.
- Give Mark short emoji-first, condensed multi-step batches with BUILD / PLAN / STOP recommendations.
- Maintain checkpoint rhythm after roughly 3–4 meaningful movements when practical.

## Build 036 Discovery Point
**Working candidate:** Price Decision Preparation Action

**Business question:** What minimum reviewed-price evidence must MarketDEX capture before the Price Decision blocker can be cleared?

Build 036 is not yet design-locked in this checkpoint.

Discovery must remain business-first and workbook-first. It must not invent automated pricing authority, marketplace publishing, or silently clear Platform, Shipping Review, or Data-Quality Clearance.

## Resume Instruction
Resume from this checkpoint and the repository foundation documents as authority.

Begin Build 036 discovery from the approved Build 035 endpoint.
Do not rediscover Builds 033–035.
Do not modify foundation documents as part of Build 036 discovery.
