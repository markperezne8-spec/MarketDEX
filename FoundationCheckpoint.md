# MarketDEX Foundation Checkpoint 060

**Status:** Active — RT-0.1 Sprint 001 Release Candidate integration

## Mandatory resume summary

MarketDEX is an offline-first, Windows-desktop collectibles business operating system. Pokémon TCG is the first optimized workflow. Continue the existing permanent codebase; do not restart it, create a competing shell, duplicate persistence authority, or treat chat memory as product authority.

Current active pull request:

- PR: `#166`
- URL: `https://github.com/markperezne8-spec/MarketDEX/pull/166`
- State: open draft
- Base: `main`
- Head: `agent/market-intelligence-foundation`

## Product Owner operating preferences

The permanent communication and delivery authority is:

- `docs/governance/AI_COLLABORATION_AND_DELIVERY_PROTOCOL.md`

Required behavior for future engineering sessions:

- show a progress bar in every meaningful milestone update
- show one clear next step
- include direct GitHub links when relevant
- distinguish planned, in-progress, committed, validated, packaged, and released work
- make routine reversible engineering decisions without unnecessary approval stops
- reserve Product Owner approval for product direction, visual direction, strategic scope, and irreversible decisions
- multitask on another safe approved track while GitHub Actions or another external dependency is pending
- use milestone-based reviews instead of constant micro-reviews
- explicitly say `READY FOR VISUAL INSPECTION — PULL NOW` or `SPRINT REVIEW READY — PULL NOW`
- state exact branch, expected commit, launch method, review scope, and known limitations when a pull is required
- update repository memory before declaring a milestone complete

When the Product Owner says `Next step`, inspect repository authority and CI, select the highest-value safe task within approved scope, proceed without unnecessary clarification, multitask when blocked, and report the next meaningful checkpoint.

## Permanent product and architecture direction

- One launcher: `launcher.py`
- One composition root: `composition/application_composition.py`
- One canonical desktop window and shell path
- One workspace registry and feature catalog
- One SQLite persistence, schema, and migration authority
- One semantic token and reusable component authority
- Windows desktop first
- Offline first
- No mandatory subscription dependency
- No prototype branch represented as the permanent product
- No presentation migration may silently change business authority
- No release without applicable source, executable, installer, installed-runtime, accessibility, visual, and checkpoint gates

## Visual and brand authority

Active Visual North Star:

- `docs/design/VISUAL_NORTH_STAR.md`
- `assets/brand/visual_north_star/marketdex_visual_north_star_v1.png`
- approved SHA-256: `1269e2af119c569cc5d4f76b82a6f92984a04f6f752119d8e1dcf417557909a5`
- approved Git blob SHA: `27d4b34b24984678225ae38c7e77240a02d521b4`

The approved PNG exists on `main`, is packaged by `MarketDEX.spec`, and is protected by the canonical brand asset packaging contract.

The permanent electric dog Pokémon mascot remains protected and must not be silently removed, replaced, or substantially redesigned.

## Completed repository-backed work in this sequence

### Visual source and package authority

- Canonical Visual North Star PNG synchronized on `main` and identity verified.
- `MarketDEX.spec` on `main` updated to package the canonical Visual North Star and mascot.
- Packaging contract test added on `main` to lock the approved asset identity and spec references.

### Mission Control visual slice on PR #166

- `ui/main_window.py` now applies the shared token theme.
- The Mission Control title surface uses `MarketDEXWorkspaceHeader`.
- The eight Mission Control KPI surfaces use `MarketDEXKpiCard`.
- Existing snapshot keys, refresh behavior, Inventory services, and SQLite reads remain preserved.
- A dedicated Mission Control CI gate was added and corrected to validate only the visual slice.
- Latest Mission Control Visual Slice job passed.

### Modern application shell on PR #166

- Boundary contract added in `tests/test_modern_application_shell_migration.py`.
- Canonical `WorkspaceHost` upgraded rather than introducing a second shell.
- Persistent branded left navigation rail added.
- Workspace content moved to a stacked workspace frame.
- Inventory, Pricing, and Listing Workflow navigation remains identity-based.
- Offline/SQLite status presentation and workspace status area added.
- Existing feature installers and compatibility aliases remain supported.

Latest shell implementation commit before this checkpoint:

- `ae89f7201cb20351f7a31dfd3cfc5eaad4635c08`
- message: `ui: modernize canonical workspace host shell`

### Permanent collaboration continuity

- `MARKETDEX_START_HERE.md` remains the canonical orientation file.
- `docs/governance/AI_COLLABORATION_AND_DELIVERY_PROTOCOL.md` records the permanent communication, multitasking, review, Definition of Ready, Definition of Done, and resume protocol.

## Latest verified CI state

Sequential RC integration is active:

- PR #164 merged to `main` at `e6a742b0732222a84986abd5032b792094f34401`.
- PR #164 post-boundary workflow passed.
- PR #165 was retargeted to `main`, repaired with the proven Listing Qt dependency and feature-catalog ordering contract, and passed fresh integrated CI.
- PR #165 merged to `main` at `c535fb5ec85e697f094552712942fa36bba6a6dd`.
- PR #166 is retargeted to `main` as the final Sprint 001 RC boundary.
- Latest fully verified PR #166 workflow before final retarget: run `29192808275`, all jobs passed, including source tests, executable packaging, packaged-runtime verification, installer build, and installed-runtime verification.

## Resolved blockers

- Desktop Build contract drift: resolved.
- Listing Linux Qt runtime dependency: resolved with explicit `libegl1` installation.
- Sale-completion ordering contract: resolved through canonical `CORE_DESKTOP_FEATURES` dependency evidence.
- Pricing legacy contrast: resolved and visually accepted.
- Listing legacy panel styling: resolved and visually accepted.
- Visual North Star source and package authority: present on `main`.

## Local source launch and review

Local repository path used by the Product Owner:

- `C:\Projects\MarketDEX_OS`

Required branch for current visual work:

- `agent/market-intelligence-foundation`

Source launch:

```powershell
cd C:\Projects\MarketDEX_OS
python -m pip install -r requirements.txt
python launcher.py
```

The Product Owner successfully installed Python and launched the source application.

Source runtime database:

- `C:\Projects\MarketDEX_OS\runtime\marketdex.sqlite3`

Installed application target after a successful future installer build:

- `%LOCALAPPDATA%\Programs\MarketDEX\MarketDEX.exe`

An existing `dist\MarketDEX.exe`, when present locally, may be older than the active branch because the current Desktop Build gate has not produced a fresh artifact.

## Current visual evidence

The Product Owner supplied a source-build screenshot. It confirmed:

- the application launches
- SQLite-backed data loads
- Inventory, Pricing, and Listing workflow structure is present
- the engineering foundation is ahead of the final Visual North Star presentation

The Product Owner approved the recommendation to modernize the canonical shell and continue with milestone-based visual transformation.

## Sprint 1 scope

Active Sprint 1 tracks:

1. Modern Application Shell
2. Mission Control visual modernization
3. Engineering continuity and self-documenting repository
4. Desktop Build contract recovery
5. Listing blocker isolation and repair
6. CI monitoring and immediate focused fixes

## Definition of Ready

A task may enter implementation only when it has:

- product and Visual North Star alignment
- clear scope and exclusions
- architecture fit
- acceptance criteria
- validation strategy
- rollback or safe-recovery approach
- documentation impact identified
- no unresolved Product Owner decision that would materially change implementation

## Definition of Done

A milestone is complete only when applicable items are true:

- implementation is committed to the intended branch
- focused tests pass
- broader CI is inspected and accurately reported
- no business-authority regression is introduced
- checkpoint and relevant governance documents are updated
- known blockers and remaining work are recorded
- next approved task is selected
- pull/review requirement is stated explicitly

## Exact next approved task

**Final PR #166 Release Candidate validation and merge.**

Execution order:

1. run the final integrated PR #166 workflow against current `main`;
2. verify Core, Inventory, Pricing, Listing, Mission Control, Desktop Build, executable, packaged runtime, installer, and installed runtime;
3. confirm no duplicate launcher, shell, database, schema, theme, or canonical governance authority;
4. mark PR #166 ready and merge only when every required gate is green;
5. verify merged `main`;
6. pull the final RC baseline and perform one narrow installed/source visual smoke check.

## Pull and review status

- Pull required now: **NO**
- Visual review required now: **NO**
- Next explicit review signal: `RT-0.1 RC READY — PULL NOW`

## Progress snapshot

- Foundation and permanent direction: `[██████████] 100%`
- Engineering continuity protocol: `[█████████░] 90%`
- Mission Control first visual slice: `[██████████] 100%` focused validation
- Modern application shell: `[██████████] 100%` visually accepted
- Desktop Build pipeline: `[██████████] 100%` on latest verified integrated run
- Windows EXE and installer: `[██████████] 100%` on latest verified integrated run
- Sprint 1 integrated readiness: `[█████████░] 95%` pending final PR #166 RC merge

## Core instruction

> Improve the existing MarketDEX foundation. Do not restart it, duplicate it, silently redefine it, or rely on chat-only memory.
