# MarketDEX Foundation Checkpoint 080

**Status:** 🏁 Checkpoint Complete — Visual North Star Dashboard-Panel Reconciliation
**Canonical branch:** `main`
**Source of truth:** GitHub repository `markperezne8-spec/MarketDEX`

## Mandatory resume summary

MarketDEX remains an offline-first Windows desktop collectibles operating system. Pokémon TCG is the first optimized workflow. Continue the existing permanent codebase; do not restart it, create a competing shell, duplicate persistence authority, or treat chat history as product authority.

The Reports foundation has advanced through controlled, read-only Inventory Age query, composition, application-boundary, catalog-routing, immutable-request, request-service integration, catalog-approved routing, request-contract hardening, immutable request-envelope integration, composition-envelope verification, catalog-to-composition presentation, result-context/source-authority slices, the Purchase Source Performance composition snapshot, the Reports workspace wiring, the Inventory Age Patterns visual preview, and the Purchase Source Performance empty-result visual surface. CAP-006 also has the read-only Collection authority card and an explicit empty-state visual surface. Reports remains offline-first, deterministic, read-only, and composition-owned; no live provider, persistence authority, cache, mutation, network behavior, export, scheduler, alert, or automation was introduced.

## Permanent operating rules

- GitHub is the source of truth.
- Use issue → branch → draft PR → CI → ready → squash-merge.
- Do not merge until the exact PR head has green CI and is mergeable.
- Tell Mark to pull only after merge.
- Require visual acceptance only for user-visible behavior.
- Preserve one launcher, one composition root, one runtime database authority, and no duplicate domain authority.
- Keep Reports offline-first, deterministic, read-only, and dependent on composition-owned approved query paths.
- Do not use Codex unless Mark explicitly requests it.

## Guidance reviewed

- `DEVELOPMENT_PLAYBOOK.md`
- `Jarvis Partnership Agreement.md`
- `Vision.md`
- `WorkbookBlueprint.md`
- `docs/WORKFLOW.md`

## Completed Reports foundation sequence

| Build | Issue | PR | CI | Merge commit | Locked result |
|---|---:|---:|---:|---|---|
| 701T | #282 | #283 | #452 | `352e0e8b` | Injected, read-only Inventory detail adapter with deterministic found/not-found/unavailable evidence. |
| 701U | #284 | #285 | #462 | `0e9e8dcc` | Application-owned Inventory Age input provider composes approved Inventory and product-link evidence. |
| 701V | #286 | #287 | #465 | `32d699b2` | Composition integration gate locked; no wiring before local synchronization. |
| 701W | #288 | #289 | #467 | `6d0b6c87` | Canonical application composition constructs the provider using Inventory's existing read-connection authority. |
| 701X | #290 | #291 | #469 | `7d2e94b2` | Future query-service contract locked: exactly one provider call and pure bridge only for verified found evidence. |
| 701Z | #294 | #295 | #473 | `a1990d2c` | Implemented immutable Inventory Age query results and injected query service with explicit outcome preservation. |
| 701AA | #296 | #297 | #475 | `2669f81e` | Composed the query service over the existing application-owned input provider without startup invocation. |
| 701AB | #298 | #299 | #479 | `7ad56e5a` | Exposed one read-only application query boundary with focused forwarding and startup-safety coverage. |
| 701AD | #302 | #303 | #483 | `27d6825c` | Bound the catalog's Inventory Age definition to the composition query boundary with unknown-report rejection. |
| 701AF | #306 | #307 | #487 | `b381d401` | Defined immutable validated Inventory Age query requests. |
| 701AG | #308 | #309 | #489 | `4a2e5fee` | Added request-based query-service entrypoint preserving one provider call and outcomes. |
| 701AH | #310 | #311 | #492 | `cd71ad4b` | Routed application composition through validated query requests. |
| 701AJ | #314 | #315 | #499 | `5c20976d` | Added deterministic catalog-approved Reports query routing while preserving the composition boundary and explicit rejection. |
| 701AL | #318 | #319 | #503 | `e34b3bcc` | Enforced the immutable Inventory Age Reports request contract at the routing boundary. |
| 701AN | #322 | #323 | #507 | `68bd3be3` | Added the immutable `ReportQueryRequest` envelope and composed it through the Reports query service. |
| 701AP | #326 | #327 | #511 | `b0e38cbc` | Verified application composition constructs and routes the immutable Reports query envelope. |
| 701BA | #341 | #341 | #536 | `db7e29db` | Added the first read-only Inventory Age result presentation surface. |
| 701BB | #342 | #342 | #538 | `3e10020c` | Preserved selected Reports context in result status. |
| 701BC | #343 | #343 | #540 | `5a92d0f1` | Made catalog-only/read-only execution status explicit in results. |
| 701BD | #344 | #344 | #542 | `db050228` | Preserved query context for non-found outcomes. |
| 701BE | #345 | #345 | #544 | `cf3eb90c` | Exposed source authority in found Inventory Age results. |
| 701BF | #346 | #346 | #546 | `b7e7efd0` | Exposed inventory source authority for all Reports outcomes; visual acceptance passed. |
| 701BI | #349 | #349 | #553 | `a210be23` | Exposed explicit source-date authority for all Reports outcomes; visual acceptance passed. |
| 701BJ | #350 | #350 | #554 | `0f2b726a` | Preserved the explicit no-Codex handover rule in the permanent workflow contract. |
| 701BP | #356 | #356 | #567 | `ed6f120f` | Exposed Inventory Age result semantics; visual acceptance completed. |
| 701BQ | #357 | #357 | #569 | `a08937bf` | Corrected missing non-found age rows; visual acceptance completed. |

All listed CI runs passed their complete required jobs, including Reports, Core Tests, Desktop Build, packaged runtime, installer build, and installed-runtime verification.

## Current architecture and authority

- `composition/application_composition.py` remains the only application composition root.
- `InventoryAppService` remains the owner of the existing runtime `database.read_connection` authority used by Build 701W.
- `ApplicationInventoryAgeInputProvider` and `InventoryAgeReportQueryService` are constructed through composition but are not invoked during startup or runtime verification.
- `ApplicationComposition.query_inventory_age(...)` is the application-level forwarding boundary for Inventory Age query results.
- `ApplicationComposition.query_report(...)` validates the catalog and routes only the supported `inventory-age-patterns` definition to that boundary.
- `ReportQueryService` is the deterministic in-memory routing boundary for catalog-approved report requests; it adds no provider, persistence, or UI authority.
- `ReportQueryService` rejects non-`InventoryAgeReportQueryRequest` values before query invocation.
- `ReportQueryRequest` is the immutable envelope joining report identity to the approved Inventory Age request.
- Application composition coverage verifies normalized report identity and Inventory Age request values reach the Reports query service.
- `InventoryAgeReportQueryRequest` is the immutable validated request value used by the query service and composition boundary.
- Inventory detail and CAP-005B product-link adapters remain the only approved evidence paths.
- Reports presentation, workspaces, and domain code do not open SQLite connections, construct database managers, query source tables directly, or repair evidence.
- The existing `build_inventory_age_row_from_input` bridge remains pure and may receive only verified found input evidence in a later query service.
- Purchase Source Performance query execution remains composition-owned and is injected into `ReportsWorkspace`.
- Reports maps Purchase Source Performance responses through the existing presentation boundary and preserves complete, unavailable, and conflicting outcomes.

## Exact next gate

**Visual North Star shell foundation work is complete through PR #759. This documentation-only reconciliation is the current controlled gate.**

Verified sequence:

1. PR #725 exposed the composition-owned Purchase Source Performance query boundary.
2. PR #727 reconciled the capability documentation.
3. PR #729 wired the query into the Reports workspace with read-only period and as-of controls.
4. PR #739 added the Inventory Age Patterns read-only visual preview with honest unavailable defaults and North Star styling.
5. PR #741 added the Collection read-only empty-state panel with explicit Product Registry + Inventory projection and blocked-write guidance.
6. PR #743 added the Purchase Source Performance read-only empty-result panel with explicit period/as-of context and no-fabricated-zero guidance.
7. PR #745 added the CAP-006 unrecorded Collection field-authority panel without adding Collection write authority.
8. PR #746 added the CAP-012 Inventory Age evidence-gate panel without changing query, evidence, or mutation authority.
9. PR #748 added the Reports catalog scope panel while reusing the existing read-only boundary text.
10. PR #755 added the branded command-center header to the canonical WorkspaceHost with presentation-only North Star styling and focused shell-contract coverage.

The next CAP-006 runtime or authority movement requires workbook-backed position authority and a separately approved issue and boundary. The next expanded Reports movement also requires a separately approved authority boundary. Preserve the approved CAP-012/CAP-006 read-only, fail-closed boundary; do not invent Collection runtime authority.

## Pull and visual status

- Pull required now: **YES after this documentation reconciliation is merged**
- Pull scope: Issue #760 Visual North Star dashboard-panel evidence reconciliation after PR #759.
- Visual review required now: **NO — PR #759 visual acceptance passed**
- ChatGPT Work required now: **NO**

## Progress snapshot

- Permanent desktop/runtime authority: `[██████████] 100%`
- Reports architecture and evidence boundaries: `[██████████] 100%`
- Inventory Age provider composition: `[██████████] 100%`
- Inventory Age query-service implementation: `[██████████] 100%` — implementation, composition wiring, and application boundary complete.
- Catalog-approved Reports routing: `[██████████] 100%` — deterministic routing boundary complete; presentation remains unauthorized.
- Reports request contract enforcement: `[██████████] 100%` — immutable request type is enforced before query invocation.
- Reports request-envelope integration: `[██████████] 100%` — report identity and approved Inventory Age request are composed immutably.
- Composition-envelope verification: `[██████████] 100%` — normalized request routing is covered.
- Reports workspace and visual presentation: `[██████████] 100%` — approved read-only surfaces, including the Inventory Age Patterns visual preview, have passed acceptance.

## Next-chat handoff

Read these repository authorities before taking action:

1. `DEVELOPMENT_PLAYBOOK.md`
2. `Jarvis Partnership Agreement.md`
3. `Vision.md`
4. `WorkbookBlueprint.md`
5. `docs/WORKFLOW.md`
6. `FoundationCheckpoint.md`
7. `CheckpointManifest.md`

Treat GitHub as the source of truth. Preserve the concise progress-bar workflow, explicit GitHub Desktop pull instructions, visual-check status, and CI → ready → squash-merge process. Do not use Codex unless Mark explicitly authorizes it. Current Reports work is UI-free; visible app changes require a separately scoped workspace build and visual review.

## Checkpoint 066 synchronization

- Build 701AJ was merged through PR #315 after CI run #499 passed all required jobs.
- Merge commit: `5c20976d06ef57c0a397999260e8bc41a699b27b`.
- No visible application change was introduced; visual review remains not required.
- Next movement remains a separately scoped UI-free Reports integration slice after local synchronization.

## Checkpoint 067 synchronization

- Build 701AL was merged through PR #319 after CI run #503 passed all required jobs.
- Merge commit: `e34b3bcc08cf4396a590461e97b5de3424065ef7`.
- No visible application change was introduced; visual review remains not required.
- Next movement remains a separately scoped UI-free Reports integration slice after local synchronization.

## Checkpoint 068 synchronization

- Build 701AN was merged through PR #323 after CI run #507 passed all required jobs.
- Merge commit: `68bd3be3d99376d6005cdbe7ea02f19a3fb23ea9`.
- No visible application change was introduced; visual review remains not required.
- Next movement remains a separately scoped UI-free Reports integration slice after local synchronization.

## Checkpoint 069 synchronization

- Build 701AP was merged through PR #327 after CI run #511 passed all required jobs.
- Merge commit: `b0e38cbcdcd26936645d51b6bad4b071c6390786`.
- No visible application change was introduced; visual review remains not required.
- Next movement remains a separately scoped UI-free Reports integration slice after local synchronization.

## Checkpoint 071 synchronization

- Builds 701BA–701BF completed the first read-only Inventory Age result-presentation sequence.
- Build 701BA introduced the result surface; Builds 701BB–701BD preserved selected report context, catalog-only status, and non-found query context.
- Build 701BE exposed source authority for found results; Build 701BF exposed `Source domain = inventory` for non-found results.
- PR #346 passed CI run #546 and was squash-merged as `b7e7efd021826698b88daad43ba0c9cad47261d0`.
- Visual acceptance passed: `Test_Inventory` produced `NOT_FOUND` with `Source domain = inventory` visible, plus outcome, reason, inventory position, and as-of date.
- Build 701BG synchronized checkpoint authority; Build 701BH records this visual acceptance and introduces no runtime or visual change.

## Core instruction

> Improve the existing MarketDEX foundation. Do not restart it, duplicate it, silently redefine it, or rely on chat-only memory.

## Checkpoint 070 synchronization

- Builds 701AR–701AZ completed the Reports catalog-to-composition milestone.
- Build 701AR added the first visible Reports workspace; PR #331, CI run #516, merge commit `4c55094b6ab744fd7c666bfb32e0e9728025b700`.
- Mark visually accepted Reports navigation and the approved `Inventory Age Patterns` catalog row; visual review is complete.
- Builds 701AS–701AZ hardened the composition-owned Reports catalog, definition, evidence, source-domain, description, and catalog-only execution-mode contracts.
- Final milestone merge: PR #339, CI run #532, merge commit `397a39c84b75309bb2592276da6c5cf34ba69ded`.
- Reports remains offline-first, deterministic, read-only, catalog-authoritative, and without live providers, persistence, export, scheduler, alert, automation, or unsupported report definitions.
- Next milestone begins from the synchronized `main` branch; any new visible result presentation or execution behavior requires a separately scoped approved build and visual review when applicable.

## Core instruction

> Improve the existing MarketDEX foundation. Do not restart it, duplicate it, silently redefine it, or rely on chat-only memory.

## Checkpoint 072 synchronization

- Build 701BF visual acceptance was completed after pull and test-position review.
- Build 701BI visual acceptance confirmed `Source date = unavailable · no Inventory detail evidence` for the deliberate NOT_FOUND result, while preserving source domain, outcome, reason, inventory position, and as-of date.
- Build 701BJ preserved the no-Codex handover rule in `docs/WORKFLOW.md`.
- Build 701BK synchronizes this checkpoint authority without changing runtime or UI behavior.
- The next Reports slice may proceed from synchronized `main`.


## Checkpoint 073 synchronization

- Build 701BI was merged through PR #349 after CI run #553 passed; merge commit `a210be2378eecb34e8cad6b11dd236c181ecbb4d`.
- Build 701BI visual acceptance passed: the NOT_FOUND result displayed `Source domain = inventory` and `Source date = unavailable · no Inventory detail evidence`, while preserving required context.
- Build 701BJ was merged through PR #350 after CI run #554 passed; merge commit `0f2b726ab64f5247b30776ba4969d609755814aa`.
- The permanent workflow now states that Codex must not be used unless Mark explicitly authorizes it in the current conversation.
- Build 701BK records the synchronized checkpoint without runtime or visual change.


## Checkpoint 074 synchronization

- Build 701BP was merged through PR #356 after CI run #567 passed; merge commit `ed6f120f4f5e252d84e7e0cc996cc45a6bf3b3e3`.
- Build 701BQ corrected the missing NOT_FOUND age rows through PR #357 after CI run #569 passed; merge commit `a08937bf9f9bf1fa9fb9706ed685c4341b3bcbae`.
- Visual acceptance passed with `Age (days) = unavailable` and `Age reason = no Inventory detail evidence`, alongside preserved source authority and query context.
- Build 701BR synchronizes this checkpoint without runtime or visual change.


## Checkpoint 076 synchronization

- M1.6 Health Monitor foundation sequence completed through Builds M1.6A–M1.6H.
- Build M1.6A introduced the immutable HealthResult contract; PR #378, CI run #611, merge commit `571f77c88275bcb4eb8bc47cf8ff77db3dd7e20e`.
- Build M1.6B introduced deterministic HealthSummary aggregation; PR #379, CI run #613, merge commit `b316604d219e8e6cf80a94e113ef380c374587bb`.
- Build M1.6C introduced deterministic HealthCheck execution; PR #380, CI run #615, merge commit `0cc8e19e855d00a8eb8a97c71ed3985c28bfb31f`.
- Build M1.6D introduced deterministic HealthSummary snapshots; PR #381, CI run #617, merge commit `1fadbb9049b8cdb29baeb7331c78686cc3e8c902`.
- Build M1.6E introduced deterministic HealthFinding extraction; PR #382, CI run #619, merge commit `cdd4e93c70246ed0e06d19287137912367fe2563`.
- Build M1.6F introduced deterministic Health report payload assembly; PR #383, CI run #621, merge commit `dca99af548164920841f778b2e0d6f19a8277b7c`.
- Build M1.6G introduced deterministic Health report text lines for logs and diagnostics; PR #384, CI run #623, merge commit `1f8b3d83f45c68129b219a3f9c0568e8a751994d`.
- Build M1.6H locked the public Health Monitor API contract; PR #385, CI run #625, merge commit `2ac2c6392102f07667e146e46a592b131e8dcdd5`.
- Health Monitor remains offline-first, deterministic, non-visual, and free of polling, persistence, network, scheduler, automation, notification, startup side effects, and business-state mutation.
- Visual check was not required for M1.6A–M1.6H.
- Codex was not used.
- Next movement may proceed from synchronized `main` after Mark pulls when back at the PC.


## M1.7 planning — Health Monitor integration readiness

M1.7 begins as a guarded Health Monitor integration-readiness milestone after the M1.6 foundation sequence.

Planning authority:

- M1.6 public exports are the approved Health Monitor API surface for future slices.
- Future M1.7 work may compose Health Monitor outputs with existing application boundaries only through explicit, deterministic, offline-first adapters.
- Any runtime integration must preserve side-effect-free behavior unless a later approved issue explicitly authorizes a side effect.
- Polling, persistence, scheduler behavior, network behavior, startup wiring, notifications, UI, and business-state mutation remain out of scope for M1.7 until separately approved.
- Non-visual contract and adapter slices do not require visual review.
- Any visible Health Monitor surface requires a separately scoped visible build and Mark visual acceptance before merge.
- Continue issue → branch → draft PR → CI → ready → squash-merge.
- Codex remains forbidden unless Mark explicitly authorizes it in the current chat.


## Checkpoint 077 synchronization

- M1.7 Health Monitor integration-readiness sequence completed through planning and Builds M1.7A–M1.7F.
- M1.7 planning defined Health Monitor integration guardrails; PR #387, CI run #629, merge commit `b7c9cadc82853dc7e035e28335c7c9b21b5bfdd3`.
- Build M1.7A introduced the immutable HealthReportProvider contract; PR #388, CI run #631, merge commit `cbe666cf5ab6f9d34edc53d2f838aa0ec5b37689`.
- Build M1.7B introduced the immutable HealthProviderBundle contract; PR #389, CI run #633, merge commit `71589ed9591f47d48abb7868feabd337bd77b6c2`.
- Build M1.7C introduced deterministic bundle-level Health summary; PR #390, CI run #635, merge commit `05d40c338316161c85f5917c7606fb5d8f6a70c9`.
- Build M1.7D introduced deterministic bundle report payload assembly; PR #391, CI run #637, merge commit `186cbed68872c6b46f2f5864f10d051ad5762fc2`.
- Build M1.7E introduced deterministic bundle report text lines; PR #392, CI run #639, merge commit `b92fcfa73dbacc3636ab04ccbd443ff7d6934263`.
- Build M1.7F locked the expanded Health Monitor integration API contract; PR #393, CI run #641, merge commit `8089e21f98d1ea6b622c7a991e32d415cbc7d726`.
- The M1.7 sequence remained non-visual and introduced no startup wiring, polling, persistence, UI, network, scheduler, automation, notifications, live checks, or business-state mutation.
- Visual check was not required for M1.7 planning through M1.7F.
- Specialist tooling was not used.
- Next movement may proceed from synchronized `main` after Mark pulls when back at the PC.


## M1.8 planning — Health Monitor runtime composition boundary

M1.8 begins as a guarded Health Monitor runtime-composition boundary after the M1.7 integration-readiness sequence.

Planning authority:

- M1.8 work may compose existing Health Monitor contracts into deterministic application-boundary helpers.
- M1.8 slices must use the approved M1.6 and M1.7 Health Monitor contracts only.
- M1.8 does not authorize startup wiring, live checks, polling, persistence, network behavior, scheduler behavior, automation, notifications, UI, or business-state mutation by default.
- Any side effect requires a separately approved issue that names the side effect explicitly.
- Non-visual composition contract slices do not require visual review.
- Any visible Health Monitor surface requires a separately scoped visible build and Mark visual acceptance before merge.
- Continue issue → branch → draft PR → CI → ready → squash-merge.
- Specialist tooling remains unused unless Mark explicitly authorizes it in the current chat.


## Checkpoint 080 synchronization — M1.14 Visual North Star alignment

- M1.14 Mission Control Visual North Star alignment completed through planning and Builds M1.14A-M1.14H.
- Planning PR #463 preserved the staged visual-only boundary; M1.14A PR #465 added the Visual North Star layout map.
- M1.14B PR #467 added North Star design tokens and panel variants.
- M1.14C PRs #469/#470 added the read-only `Command Status` header/status band shell.
- M1.14D PR #472 added the North Star left navigation visual treatment while preserving existing workspace routes.
- M1.14E PR #474 added the read-only `Dashboard Grid` shell below `Next Steps`.
- M1.14F PR #476 added the read-only `Inventory Command Center` shell using existing local Units, Assets, and Cost evidence only.
- M1.14G PR #478 added the read-only `Visual Intelligence` shell with unavailable chart, alert, heat map, and trend regions.
- PR #480 fixed the M1.14 dashboard right-edge clipping by wrapping Inventory Command Center future-contract cards.
- PR #482 fixed launch behavior so MarketDEX opens maximized.
- Visual acceptance passed for the left rail, Command Status, Dashboard Grid, Inventory Command Center, Visual Intelligence shell, resize behavior, and launch-maximized behavior.
- M1.14 introduced no fake live values, marketplace providers, networking, polling, background workers, alerts, notifications, automation, task execution, mutation controls, persistence changes, database migration, dependency changes, route rewrites, new workspaces, or business-state mutation.
- Remaining North Star business-intelligence areas require future contracts before real values appear.
- M1.14H records this acceptance and introduces no runtime or UI behavior change.

## Current next gate

The next build may proceed from synchronized `main` after Mark pulls. Future visible work must continue using the GitHub-first issue -> branch -> draft PR -> CI -> ready -> squash-merge process and requires screenshot acceptance. Future real values for remaining North Star regions require dedicated immutable view-model or service contracts before display.

## M1.15 planning - Mission Control Today's Top 3 attention contract

M1.15 begins as the next guarded Mission Control North Star milestone after M1.14 visual acceptance.

Planning authority:

- The target surface is a future read-only `Today's Top 3` / attention-priority region.
- The future surface should answer: `What deserves attention first today?`
- Real priority items require an immutable view-model or service contract before display.
- Future evidence must be prepared/injected and local-only; missing evidence must render `Unavailable` or `Partial`.
- Planned states are `Ready`, `Unavailable`, `Partial`, and `Error-safe`.
- `Today's Top 3` must complement, not duplicate, the existing `Next Steps` surface.
- Future visible builds require screenshot acceptance.
- Planning introduces no runtime code, UI implementation, ranking engine, fake live values, task execution, action buttons, automation, polling, background workers, networking, marketplace/live pricing, persistence changes, database migration, alerts, notifications, route rewrites, new workspaces, dependency changes, or business-state mutation.
- Continue issue -> branch -> draft PR -> CI -> ready -> squash-merge.

## M1.15D verification - Today's Top 3 visual and contract acceptance

M1.15D records accepted visual and contract evidence for the `Today's Top 3` attention-priority surface.

Verified result:

- M1.15A PR #488 added the immutable non-visual attention-priority view-model contract.
- M1.15B PR #490 added the first visible read-only `Today's Top 3` shell.
- M1.15C PR #492 hardened deterministic display and contract state; CI run #29562275992 passed before merge.
- Mark supplied accepted screenshots after the M1.15B and M1.15C runs.
- The accepted placement is after `Next Steps` and before `Dashboard Grid`.
- The default missing-evidence state remains honest `Unavailable` output.
- The three priority cards render as deterministic `#1`, `#2`, and `#3` read-only unavailable cards.
- M1.15D introduces no runtime or UI behavior change and requires no additional visual check.

M1.15 remains protected from action buttons, task execution, ranking-engine behavior beyond deterministic display ordering, fake live values, marketplace or live-pricing integration, polling, background workers, networking, persistence changes, database migration, alerts, notifications, automation, route rewrites, new workspaces, dependency changes, or business-state mutation.

## M1.15E synchronization - Today's Top 3 sequence complete

M1.15E synchronizes repository authority after the completed `Today's Top 3` attention-priority sequence.

Completed sequence:

- M1.15 planning PR #486 locked the contract-first milestone.
- M1.15A PR #488 added the immutable non-visual view-model contract.
- M1.15B PR #490 added the visible read-only shell.
- M1.15C PR #492 hardened deterministic display states.
- M1.15D PR #494 recorded visual and contract verification; merge commit `dee1e248f37eb06b4f2557351f08c60df54f168b`.

Final accepted behavior:

- `Today's Top 3` appears after `Next Steps` and before `Dashboard Grid`.
- Default missing evidence renders honest `Unavailable` output.
- Priority slots `#1`, `#2`, and `#3` are deterministic, read-only, and unavailable by default.
- Visual acceptance is complete through accepted M1.15B and M1.15C screenshot evidence recorded by M1.15D.
- M1.15E introduces no runtime behavior, UI change, view-model change, test change, persistence change, dependency change, route change, workspace change, or business-data mutation.

Current next gate:

- The next build may proceed from synchronized `main` after Mark pulls.
- Future real `Today's Top 3` values require a separately approved local evidence contract and focused implementation slice.
- Future North Star areas remain contract-first and must be scoped independently.

## M1.16 planning - Mission Control Capital Health contract

M1.16 begins as the next guarded Mission Control North Star milestone after the completed M1.15 `Today's Top 3` sequence.

Planning authority:

- The target surface is a future read-only `Capital Health` region.
- The future surface should answer: `Is business capital available, recycling, committed, and growing?`
- Capital Health must preserve the approved dimensions: Availability, Recycling, Commitment, and Growth.
- Available Cash remains distinct from Available for Redeployment.
- Capital Health should explain dimensions, not collapse them into one opaque score.
- Capital Growth measures business-cycle growth, not external cash injection.
- Capital Recycling Rate remains protected and unresolved at the exact formula level.
- Real values require an immutable view-model or service contract before display.
- Future evidence must be prepared/injected and local-only; missing evidence must render `Unavailable` or `Partial`.
- Planned states are `Ready`, `Unavailable`, `Partial`, and `Error-safe`.
- Planning introduces no runtime code, UI implementation, capital calculation, financial-provider integration, fake cash values, fake capital values, fake growth/trend/recycling values, task execution, action buttons, automation, polling, background workers, networking, marketplace/live pricing, persistence changes, database migration, alerts, notifications, route rewrites, new workspaces, dependency changes, or business-state mutation.
- Continue issue -> branch -> draft PR -> CI -> ready -> squash-merge.

## M1.16D verification - Capital Health visual and contract acceptance

M1.16D records accepted visual and contract evidence for the Mission Control `Capital Health` surface.

Verified result:

- M1.16A PR #500 added the immutable non-visual Capital Health view-model contract.
- M1.16B PR #502 added the first visible read-only `Capital Health` shell.
- M1.16C PR #504 hardened deterministic display states, labels, tones, group ordering, and inline error-safe rendering; CI run #760 passed before merge.
- Mark supplied accepted screenshot evidence after the M1.16B run.
- The accepted placement is after `Today's Top 3` and before `Dashboard Grid`.
- The default missing-evidence state remains honest `Unavailable` output.
- Availability, Recycling, Commitment, and Growth render as deterministic read-only groups.
- Available Cash remains visibly distinct from Available for Redeployment.
- M1.16D introduces no runtime or UI behavior change and requires no additional visual check.

M1.16 remains protected from action controls, task execution, popup or dialog behavior from the Capital Health surface, formula invention, fake cash values, fake capital values, fake growth/trend/recycling/commitment values, financial-provider integration, marketplace or live-pricing integration, polling, background workers, networking, persistence changes, database migration, alerts, notifications, automation, route rewrites, new workspaces, dependency changes, or business-state mutation.


## M1.20A checkpoint synchronization

- M1.20A was merged through PR #542 after CI run #806 passed all 9 required jobs.
- PR head: `d1deb12fe6937f831c3ce4ae475a4ae518f13dd2`; merge SHA: `771c4fbe51e0d73a426faa034356ae6137cbc9bc`.
- The immutable Data Freshness contract and focused tests are present on `main`.
- The merged correction restores clean syntax in `ui/main_window.py`.
- Direct post-merge source verification confirmed all three intended paths on `main`.
- Visual review was not required for M1.20A.
- Next separately scoped build: M1.20B decision and possible visible read-only shell.


## Repository hygiene and CI guard synchronization

- PR #546 locked the canonical runtime authority guard after CI run #811 passed all 9 required jobs; merge commit `ccf7fc48d45b74cacc8093c6bf5f6d1a12b878b8`.
- PR #548 added explicit `.gitignore` protection for local Codex/Pytest scratch folders after CI run #813 passed all 9 required jobs; merge commit `90bd416228e35991b9a019ed62dfdcb00f9a042f`.
- PR #550 stabilized Python dependency cache keys after CI run #815 passed all 9 required jobs; merge commit `601f61556be927c64fd08a6c214da90b48971e30`.
- PR #552 added the CI workflow gate inventory guard after CI run #817 passed all 9 required jobs; merge commit `1d837b6355b232770d27c12d7cbf3dc1024f14b3`.
- The canonical root runtime remains protected: `launcher.py`, root `composition/`, root `ui/`, and root `services/`.
- Legacy `app/` runtime trees remain explicitly noncanonical and must not be deleted by assumption.
- CI acceleration is now guarded against silently removing required job ids, cache dependency paths, Desktop contract gate, packaged runtime verification, installer build, installed runtime verification, or installer artifact upload.
- Visual review was not required for this repository-hygiene and CI-governance sequence.
- Pull required locally: **YES when Mark is back at the PC**: GitHub Desktop -> `main` -> Fetch origin -> Pull origin.
- Next movement may proceed from synchronized GitHub `main`; local runtime or visual checks should wait until Mark pulls.


## CAP-012 Reports synchronization — PRs #718 and #720

- PR #718 delivered the composition-owned, immutable Purchase Source Performance presentation snapshot and passed the required visual acceptance.
- PR #720 reconciled CAP-012AN documentation with the delivered canonical acquisition projection and report adapter; its documentation-only CI passed.
- CAP-012 remains `Partial`. Live provider execution, expanded queries, charts, exports, persistence, and automation remain separately gated.

- Main is synchronized at merge commit `438d30924aa3c64d550d05bc9ee36688b741a295` before this documentation sync.
- No visual check is required for this documentation-only boundary.


## CAP-012 Reports synchronization — PRs #725, #727, and #729

- PR [#725](https://github.com/markperezne8-spec/MarketDEX/pull/725) exposed the composition-owned Purchase Source Performance query boundary.
  - Exact head: `8267337be13acdf9e99cc632488ed1a73a619866`
  - CI [#1013](https://github.com/markperezne8-spec/MarketDEX/actions/runs/31776779701) passed.
  - Merge commit: `4e1b0fa073d6695f37760d5e8d7e3c5b2a0ca1bb`.
- PR [#727](https://github.com/markperezne8-spec/MarketDEX/pull/727) reconciled the capability documentation.
  - Exact head: `be7ae1957b9682e3d8c16c263e50967a5ee8721f`
  - CI [#1015](https://github.com/markperezne8-spec/MarketDEX/actions/runs/31777796443) passed.
  - Merge commit: `409674ef1bbe5e48728af933c237a00dad879e4f`.
- PR [#729](https://github.com/markperezne8-spec/MarketDEX/pull/729) wired the existing query into the Reports workspace.
  - Exact head: `c5b67daac4c175242dafb1608defde3f487a7f46`
  - CI [#1017](https://github.com/markperezne8-spec/MarketDEX/actions/runs/31787132407) passed for that exact head.
  - Scope was limited to `ui/reports_workspace.py`, `composition/application_composition.py`, and `tests/test_reports_workspace.py`.
  - Visual acceptance passed from the maximized full-window Reports screenshot.
  - Merge commit: `941c65ca4730f052a9f2f9bb9978de99fe74afaa`.
- CAP-012 remains offline-first, deterministic, read-only, composition-owned, and without live providers, persistence, exports, schedulers, alerts, automation, or business-state mutation.
- CAP-006 Collection remains unchanged by this sequence and requires its own approved boundary before runtime work.

## Current controlled next gate

After this synchronization is merged and pulled, the next CAP-012 Reports movement must be separately approved and separately scoped. No duplicate PR or runtime path is authorized.


## CAP-006E — Collection Visual Authority Evidence Synchronization

- Issue [#738](https://github.com/markperezne8-spec/MarketDEX/issues/738) records the accepted visual evidence for the merged Collection authority-card build.
- PR [#737](https://github.com/markperezne8-spec/MarketDEX/pull/737) introduced the read-only Collection Position Projection authority card and removed the Collection table row-number gutter.
- Exact PR head: `b5c7c78304a67c224419be3f38499e68964c36d2`.
- CI [#1034](https://github.com/markperezne8-spec/MarketDEX/actions/runs/31954583951) passed for that exact head.
- Merge commit: `dadadf0da7c197d784f986405b4e22e4284c22f3`.
- Mark accepted the maximized screenshot: readable READ-ONLY and AUTHORITY GATE labels, Product Registry + Inventory projection evidence, aligned controls, and no numbered row gutter.
- CAP-006 remains Partial and read-only. No Collection persistence, CRUD, inference, valuation, lifecycle mutation, Inventory conversion, provider, network, export, automation, or business-state mutation authority was introduced.
- This CAP-006E synchronization changes documentation only; no new visual check is required.
- After merge, GitHub Desktop should be synchronized to the merge commit before the next build.


## 🏁 Checkpoint 073 — CAP-012 Reports preview and CAP-006 Collection evidence

- Issue [#740](https://github.com/markperezne8-spec/MarketDEX/issues/740) records this documentation-only synchronization boundary.
- Main baseline before this branch was merge commit `6b9de6cbe9f2dcdd14b32506a2afe733db1f9a34`.
- PR [#739](https://github.com/markperezne8-spec/MarketDEX/pull/739) added the Inventory Age Patterns read-only visual preview panel.
- Exact PR #739 head: `8da4873f2f4a0c5f328eb1c6e5a53efa2654fce1`.
- CI [#1041](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32332846188) passed for that exact head.
- PR #739 squash merge commit: `6b9de6cbe9f2dcdd14b32506a2afe733db1f9a34`.
- Mark accepted the maximized Reports screenshot: navy/blue North Star panel and cards, honest `Unavailable` values, inventory source context, evidence wording, and `no mutation authority`.
- CAP-012 remains Partial with the three approved Reports boundaries; no fourth report, expanded query, live provider, export, persistence, automation, or mutation authority was introduced.
- CAP-006 remains Partial and read-only. PR #738 reconciled the accepted PR #737 Collection authority-card evidence; Collection remains blocked on workbook-backed position grain, field vocabulary, evidence ownership, lifecycle, and Inventory transition authority.
- This synchronization changes documentation only and requires no new visual check.
- Next controlled gate: any further CAP-012 expansion or CAP-006 runtime/authority change requires a separately approved, separately scoped issue.


## 🏁 Checkpoint 074 — CAP-006 Collection empty-state evidence

- Issue [#742](https://github.com/markperezne8-spec/MarketDEX/issues/742) records this documentation-only synchronization boundary.
- Main baseline before this branch was merge commit `88f11e9968ddbcd40beb1653f32d1525a81592dc`.
- PR [#741](https://github.com/markperezne8-spec/MarketDEX/pull/741) added the Collection read-only empty-state panel and visibility transitions for empty, unmatched, and populated results.
- Exact PR #741 head: `7881cfbae8ee145b5c83b8383d70947cd6ea52ee`.
- CI [#1045](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32578607084) passed for that exact head.
- PR #741 squash merge commit: `88f11e9968ddbcd40beb1653f32d1525a81592dc`.
- Mark accepted the maximized Collection Overview screenshot: navy/blue panel styling, clear `No linked Collection positions` state, Product Registry + Inventory projection wording, blocked-write guidance, preserved authority card, and intact results table.
- CAP-006 remains Partial and read-only. The panel improves comprehension only; it does not authorize Collection persistence, CRUD, lifecycle, inference, valuation, Inventory conversion, or mutation.
- This synchronization changes documentation only and requires no new visual check.
- Next controlled gate: any CAP-006 runtime/authority change requires the blocked workbook-backed decisions to be approved first.

## 🏁 Checkpoint 075 — CAP-012 Purchase Source Performance empty-state evidence

- Issue [#744](https://github.com/markperezne8-spec/MarketDEX/issues/744) records this documentation-only synchronization boundary.
- Main baseline before this branch was merge commit `1b9ca2577e7542b0c80bc4340c391da9ac526659`.
- PR [#743](https://github.com/markperezne8-spec/MarketDEX/pull/743) added the Purchase Source Performance read-only empty-result panel and populated-row visibility coverage.
- Exact PR #743 head: `988934ab4c21581a463866aadd19caed1c0e8af1`.
- CI [#1049](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32688317552) passed for that exact head.
- PR #743 squash merge commit: `1b9ca2577e7542b0c80bc4340c391da9ac526659`.
- Mark accepted the maximized Reports screenshot showing the navy/blue panel, zero source rows, period/as-of context, read-only controls, intact table, and explicit `missing evidence is not converted to zero` wording.
- CAP-012 remains Partial and read-only. No new report, query, persistence, export, networking, automation, or mutation authority was introduced.
- This synchronization changes documentation only and requires no new visual check.
- Next controlled gate: any further CAP-012 expansion requires a separately approved workbook-backed boundary.


## 🏁 CAP-006 and CAP-012 synchronization after PRs #745 and #746

- Issue [#747](https://github.com/markperezne8-spec/MarketDEX/issues/747) records this documentation-only synchronization boundary.
- Main baseline before this branch was merge commit `7a591bf7cdcb16454ec9d29eea463758133c2d5c`.
- PR [#745](https://github.com/markperezne8-spec/MarketDEX/pull/745) delivered the CAP-006 read-only field-authority panel.
- Exact PR #745 head: `a8e529fc082429535e889c8d3b6a098e08de594b`.
- CI [#1053](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32695854552) passed for that exact head.
- PR #745 squash merge commit: `3afe559292cac3d3b0f5f905d95b45d89bb9d01c`.
- Mark accepted the maximized Collection Overview screenshot showing `Unrecorded Collection fields`, the explicit `Not recorded` authority boundary, the Product Registry + Inventory projection, and no Collection writes.
- CAP-006 remains Partial and read-only; workbook-backed position grain, field vocabulary, evidence ownership, lifecycle, and Inventory transition authority remain unresolved.
- PR [#746](https://github.com/markperezne8-spec/MarketDEX/pull/746) delivered the CAP-012 Inventory Age evidence-gate panel.
- Exact PR #746 head: `4ff7bbc5c9b8319a7b9b13be82e5b2ad2ef6b652`.
- CI [#1055](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32698189459) passed for that exact head.
- PR #746 squash merge commit: `7a591bf7cdcb16454ec9d29eea463758133c2d5c`.
- Mark accepted the maximized Reports screenshot showing `Inventory Age evidence gate`, `CATALOG-ONLY · UNAVAILABLE`, unavailable metrics, source context, and the wording that missing detail evidence leaves age unavailable and conflicting evidence blocks numeric output.
- CAP-012 remains Partial and read-only; the approved three-report set and explicit unavailable/conflicting/no-fabricated-value semantics are preserved.
- This synchronization changes documentation only and requires no new visual check.
- Next controlled gate: any further CAP-006 runtime/authority movement or CAP-012 expansion requires a separately approved, separately scoped workbook-backed boundary.


## 🏁 CAP-012 catalog scope synchronization after PR #748

- Issue [#749](https://github.com/markperezne8-spec/MarketDEX/issues/749) records this documentation-only synchronization boundary.
- Main baseline before this branch was merge commit `97d9718123b677708adb76371a3d61bfe77de36e`.
- PR [#748](https://github.com/markperezne8-spec/MarketDEX/pull/748) delivered the compact `Approved report catalog` scope panel above the existing Reports summary cards.
- Exact PR #748 head: `ffeffe750ceefd6cb6d6983e34c21800d4520f11`.
- CI [#1059](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32886676226) passed for that exact head.
- PR #748 squash merge commit: `97d9718123b677708adb76371a3d61bfe77de36e`.
- Mark accepted the maximized Reports screenshot showing the approved report catalog panel, preserved catalog-only/composition-owned status text, three approved report cards, intact report table, and North Star styling without clipping.
- CAP-012 remains Partial and read-only. The three approved report definitions, unavailable/conflicting evidence semantics, no-fabricated-value rule, and composition-owned query boundary remain unchanged.
- This synchronization changes documentation only and requires no new visual check.
- Next controlled gate: any further CAP-012 expansion requires a separately approved workbook-backed boundary.


## 🏁 CAP-012 read-only preview state synchronization after PR #750

- Issue [#751](https://github.com/markperezne8-spec/MarketDEX/issues/751) records this documentation-only synchronization boundary.
- Main baseline before this branch was merge commit `f5f9c7a6b0c7b951caf95c1131516e4c2e2e4de6`.
- PR [#750](https://github.com/markperezne8-spec/MarketDEX/pull/750) delivered consistent `READ-ONLY PREVIEW` labels across the Inventory Age Patterns, Inventory Turnover, and Purchase Source Performance panels.
- Exact PR #750 head: `caac9d1457b3189a560af5e21ba5df2f035dfd24`.
- CI [#1063](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32893850196) passed for that exact head across all nine required gates.
- PR #750 squash merge commit: `40cf9b7a6c65373519f2ba979cdc5728fa658c79`.
- Mark accepted maximized Reports screenshots confirming all three labels, preserved metrics and empty-result semantics, intact controls, no clipping, and North Star styling.
- CAP-012 remains Partial and read-only. No new report definition, query, provider, persistence, export, networking, automation, or mutation authority was introduced.
- This synchronization changes documentation only and requires no new visual check.
- Next controlled gate: any further CAP-012 expansion requires a separately approved workbook-backed boundary.


## Checkpoint 076 — CAP-012/CAP-006 regression boundary synchronization

- PR [#752](https://github.com/markperezne8-spec/MarketDEX/pull/752) delivered focused regression coverage for the approved Reports and Collection read-only boundary.
- Exact PR #752 head: `ceac91e5b623cc245c5d80b73d189332f6cb9dbd`.
- CI [#1068](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32937077082) passed all nine required jobs, including Reports, Collection, Core Tests, and Desktop Build.
- PR #752 squash merge commit: `cc2ae18e5b1e67320791181dd3bcc3ee4334a4cb`.
- Scope was limited to `tests/test_build701ar_reports_workspace.py` and `tests/test_cap006_collection_position_workspace.py`.
- CAP-012 remains Partial, read-only, composition-owned, and fail-closed. The tests preserve non-editable report surfaces and unavailable/conflicting evidence semantics.
- CAP-006 remains Partial and read-only. The tests preserve the refresh-only Collection projection and unrecorded Condition / Grade and Collector Intent boundary.
- No new report, Collection authority, UI behavior, persistence, export, networking, automation, or mutation authority was introduced.
- This synchronization is documentation-only and requires no visual check.
- Next controlled gate: any runtime expansion still requires a separately approved workbook-backed boundary.


## Checkpoint 077 top-level authority normalization

- Current main: `5fe59155cee74b79406ab0c7e3356919a24a1d5c`.
- PR [#753](https://github.com/markperezne8-spec/MarketDEX/pull/753) reconciled PR #752 regression evidence across the permanent records.
- This issue aligns the top-level status and resume gate with the already merged PR #753 evidence.


## Checkpoint 078 synchronization

- PR [#755](https://github.com/markperezne8-spec/MarketDEX/pull/755) added the branded command-center header to the canonical `WorkspaceHost`.
- Exact PR #755 head: `c46bc244d3d28efe568114302264e09a5c1db82c`.
- CI [#1074](https://github.com/markperezne8-spec/MarketDEX/actions/runs/33030902498) passed all nine required gates.
- Squash merge commit: `b6d40ab7f75dcb445dbff5ca286754b9e855c46c`.
- Accepted maximized Mission Control screenshot confirms `MarketDEX OS`, `COMMAND CENTER`, `LOCAL AUTHORITY`, `OFFLINE FIRST`, persistent navigation, and no clipping or overlap.
- The change is presentation-only: services, data, commands, workspace IDs, launcher, composition root, and authority boundaries remain unchanged.
- CAP-006 and CAP-012 remain Partial/read-only and fail-closed; no new workbook-backed authority was introduced.
- PR [#756](https://github.com/markperezne8-spec/MarketDEX/pull/756) records this documentation reconciliation; no additional visual check is required.


## Checkpoint 079 synchronization

- Current main after PR #757: `806c11693e416ed5f93f039682f15d80cce503e3`.
- PR [#757](https://github.com/markperezne8-spec/MarketDEX/pull/757) delivered the Visual North Star persistent navigation-rail grouping and semantic accents.
- Exact PR #757 head: `30d08d2aad7864af574d650678dfd3c8293fcf80`.
- CI [#1079](https://github.com/markperezne8-spec/MarketDEX/actions/runs/33036161560) passed all nine required gates, including Mission Control Visual Slice and Desktop Build.
- Squash merge commit: `806c11693e416ed5f93f039682f15d80cce503e3`.
- Mark accepted the maximized Mission Control screenshot showing OPERATIONS, COLLECTION, and INTELLIGENCE group labels, related workspaces adjacent, semantic left accents, preserved shell hierarchy, and no clipping or overlap.
- The presentation-only scope preserved workspace IDs, routes, activation, services, data, commands, launcher, composition root, and the read-only CAP-006/CAP-012 boundaries.
- CAP-006 and CAP-012 remain Partial, read-only, composition-owned where applicable, and fail-closed. No workbook-backed authority was inferred.
- PR [#758](https://github.com/markperezne8-spec/MarketDEX/issues/758) records this documentation-only synchronization; no additional visual check is required.
- Next controlled gate: any CAP-006 runtime/authority movement or expanded CAP-012 behavior still requires a separately approved workbook-backed boundary.


## Checkpoint 080 synchronization

- Current main after PR #759: `ea7f993a7164d8ac897619a77e854462c7230615`.
- PR [#759](https://github.com/markperezne8-spec/MarketDEX/pull/759) delivered semantic Visual North Star accent rails for reusable dashboard panels.
- Exact PR #759 head: `c2ab9f04f46aff998680d35edea8666f2b3e28ce`.
- CI [#1083](https://github.com/markperezne8-spec/MarketDEX/actions/runs/33037632359) passed all nine required gates, including Mission Control Visual Slice and Desktop Build.
- Squash merge commit: `ea7f993a7164d8ac897619a77e854462c7230615`.
- Mark accepted the maximized Mission Control screenshot showing semantic panel accents, preserved KPI and read-only content, intact North Star hierarchy, and no clipping or overlap.
- The presentation-only scope preserved workspace IDs, routes, activation, services, data, commands, launcher, composition root, and capability authority.
- CAP-006 and CAP-012 remain Partial, read-only, composition-owned where applicable, and fail-closed. No workbook-backed authority was inferred.
- PR [#760](https://github.com/markperezne8-spec/MarketDEX/issues/760) records this documentation-only synchronization; no additional visual check is required.
