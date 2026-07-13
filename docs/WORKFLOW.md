# MarketDEX Build Workflow

This document is the permanent operating contract for ChatGPT-led MarketDEX development.

## Source of truth

- GitHub repository: `markperezne8-spec/MarketDEX`
- Local working path: `C:\Projects\MarketDEX_OS`
- GitHub is always the source of truth.
- Do not use Codex unless the user explicitly requests it.

## Permanent guidance set

Before selecting a new milestone or runtime capability, review:

- `Vision.md` for product purpose, comprehension, business-value, history, and offline-first guidance;
- `WorkbookBlueprint.md` for workbook authority and proven business workflow guidance;
- `docs/WORKFLOW.md` for the permanent delivery and communication contract.

If a required guidance file cannot be located on current `main`, record that gap in the active checkpoint and resolve it before authorizing runtime implementation.

## Response contract

- Keep responses concise and action-oriented.
- Always show a progress bar.
- Always identify the current build, issue, branch, PR, head commit, and CI run when available.
- Always include a direct clickable link to the active GitHub Actions CI run.
- State clearly whether the user should pull now or not.
- State clearly whether a visual check is required or not.

## Build workflow

1. Inspect GitHub `main` and the current architecture/build record before choosing the next slice.
2. Create or confirm a narrowly scoped issue.
3. Create the build branch from current `main`.
4. Implement the smallest coherent change.
5. Open a draft PR.
6. Wait for CI. While CI runs, a non-conflicting documentation or prebuild slice may proceed in parallel.
7. If CI fails, inspect the exact failed job and logs, apply the smallest grounded repair, and rerun validation.
8. Do not mark ready or merge until CI is green.
9. Mark ready and squash-merge with the expected head SHA.
10. Tell the user exactly when to pull through GitHub Desktop.
11. Require a visual check only for user-visible UI behavior.
12. After visual confirmation, continue to the next build.

## Pull instructions

When a merged build is ready locally:

1. Open GitHub Desktop.
2. Select the MarketDEX repository.
3. Confirm branch `main`.
4. Click **Fetch origin**.
5. Click **Pull origin**.
6. Wait until GitHub Desktop reports the branch is up to date.

Never instruct the user to pull an unmerged draft branch.

## Visual verification

- UI changes require an explicit visual-check checklist after merge and pull.
- Internal contracts, tests, documentation, CI, and non-visual architecture changes do not require a visual check.
- If the screenshot is correct, explicitly record the visual check as passed before advancing.

## Architecture discipline

- Preserve one permanent codebase.
- Prefer composition-owned services and registries.
- Do not add duplicate service paths, hidden singletons, UI-owned data authorities, or parallel registries.
- Audit wiring before rewiring.
- Rewire only when duplicate construction, bypassed composition, conflicting ownership, or hidden global state is proven.
- Keep MarketDEX offline-first and provider-neutral unless a later build explicitly authorizes otherwise.
- Do not introduce persistence, live providers, automation, alerts, schedulers, or mutation authority without an approved build boundary.

## Multitasking rule

While one PR is waiting on CI, another build may start only when it is clearly non-conflicting. Prefer documentation, architecture classification, or tests that do not touch the same files or authority path.

## Mandatory checkpoints

Create a repository checkpoint when the user requests one and at major milestone boundaries. The checkpoint must record:

- builds, issues, PRs, CI runs, and merge commits completed during the session;
- architecture and authority decisions learned;
- guidance files reviewed;
- unresolved evidence or path gaps;
- the exact next build gate;
- pull and visual-check status.

A checkpoint is documentation evidence. It does not authorize new runtime, persistence, network, UI, or mutation scope.

## Merge rule

Use squash merge only after:

- the PR is no longer draft;
- all required CI checks are green;
- mergeability is confirmed;
- the expected head SHA has not changed.


## Future chat handover rule

Every future MarketDEX chat must preserve this operating rule:

- GitHub is the source of truth.
- Codex must not be used unless Mark explicitly authorizes it in the current conversation.
- The default handover state is **No Codex**.
- Future chats must read this workflow contract and the required checkpoint documents before taking action.


## Accelerated batch-build rhythm

When Mark requests faster progress, future chats may bundle up to three tightly related, non-conflicting micro-features into one build.

The accelerated rhythm uses:

1. One narrowly scoped issue, branch, draft PR, and CI gate.
2. One consolidated visual check when the batch changes visible behavior.
3. One checkpoint synchronization after the batch.
4. The same CI → ready → squash-merge and GitHub Desktop pull rules.

Do not batch unrelated architecture, authority, persistence, migration, provider, or automation changes. Preserve composition ownership, explicit non-goals, and the smallest coherent build boundary.
