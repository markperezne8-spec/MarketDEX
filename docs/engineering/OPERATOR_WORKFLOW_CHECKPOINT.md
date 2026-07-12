# MarketDEX Operator Workflow Checkpoint

Status: Active checkpoint
Purpose: preserve the operator's preferred communication, GitHub, CI, pull, visual-check, and ChatGPT Work handoff workflow for future MarketDEX chats.

## Operator communication preferences

- Be direct, practical, and action-oriented.
- Prefer short status updates over long theory.
- Use exact commands when the operator needs to act locally.
- Clearly separate what has already happened, what is happening now, and what the operator must do next.
- Avoid asking for confirmation when the next step is already authorized by the current workflow.
- Call out uncertainty or blocking conditions immediately.
- Do not hide failures. If a command, CI run, merge, or cleanup failed, say so plainly and give the next safe recovery step.

## Progress bar format

Every major status update should include a lightweight progress reference when useful:

```text
Collector Foundation   ███████████████████░  95%
Market Intelligence    ██████████░░░░░░░░░░  50%
Business Operations    ███░░░░░░░░░░░░░░░░░  15%
Desktop Experience     ████░░░░░░░░░░░░░░░░  20%
Jarvis Automation      ███░░░░░░░░░░░░░░░░░  15%
```

The percentages are planning references, not strict product metrics. Update them only when a meaningful milestone lands.

## Standard GitHub workflow

Use GitHub as the canonical source of truth.

Preferred build flow:

1. Create or identify the issue.
2. Create a focused branch from `main`.
3. Make the smallest authorized change.
4. Open a draft PR.
5. Wait for CI.
6. If CI passes, mark the PR ready.
7. Squash-merge.
8. Tell the operator to pull.
9. Only after the operator confirms local sync, proceed to the next merge-dependent build.

Draft PRs are preferred while CI is running. Do not merge a draft PR. Mark it ready only after CI is green and the change is still appropriate.

## Pull timing rule

Tell the operator to pull only after a PR is merged into `main`.

Use this exact local sync block unless a special branch checkout is required:

```powershell
cd C:\Projects\MarketDEX_OS
git switch main
git pull origin main
git status -sb
```

A clean synced result may still show permission warnings for `.codex-pytest-tmp*`. Those warnings are not source-code changes.

Do not tell the operator to pull while:

- a PR is still in draft;
- CI is still running;
- a branch is open but unmerged;
- the work exists only on a feature branch.

## Visual check rule

Only request a visual check when a build changes visible application behavior.

Use the exact marker:

```text
VISUAL CHECK REQUIRED
```

A visual check is required for changes to:

- desktop workspace screens;
- navigation;
- buttons, tables, dialogs, controls, charts, or layout;
- window behavior;
- styling, themes, or visual density;
- packaged runtime behavior that must be opened by the operator.

A visual check is not required for:

- documentation-only builds;
- service-layer changes;
- repository or domain tests;
- CI workflow changes;
- architecture locks;
- provider-neutral backend contracts with no visible UI.

When a visual check is required, tell the operator exactly what screen to open and what to verify.

## ChatGPT Work handoff rule

Prompt the operator to switch to ChatGPT Work when the task benefits from heavier coding help, Codex-style local implementation, or deeper project editing.

Switch to ChatGPT Work for:

- larger multi-file coding or refactors;
- local test failures that need hands-on debugging;
- packaging, installer, PyInstaller, or Windows runtime errors;
- UI work that needs iterative visual inspection;
- tasks requiring local filesystem context not available through the GitHub connector;
- situations where the repository connector is not enough to confidently implement and verify the change.

Remain in the current chat for:

- GitHub issue, branch, PR, CI, and merge coordination;
- small documentation or architecture changes;
- small focused service/test slices that can be safely edited through GitHub;
- roadmap and workflow planning.

When recommending ChatGPT Work, say why it is needed and what the operator should bring over, such as the repo path, PR number, failing command, or screenshot.

## Local repository conventions

Primary local repo path:

```text
C:\Projects\MarketDEX_OS
```

Default branch:

```text
main
```

Remote:

```text
https://github.com/markperezne8-spec/MarketDEX.git
```

If the operator sees `fatal: not a git repository`, they are likely in the wrong directory. Tell them to run:

```powershell
cd C:\Projects\MarketDEX_OS
```

## Codex temp folder warnings

The operator's local repo may show warnings like:

```text
warning: could not open directory '.codex-pytest-tmp/': Permission denied
```

Known folders include:

- `.codex-pytest-tmp`
- `.codex-pytest-tmp-2`
- `.codex-pytest-tmp-4`
- `.codex-pytest-tmp-5`

Treat these as local permission-locked temporary folders, not MarketDEX source changes. They do not block Git sync, GitHub CI, or normal repository work.

Only attempt cleanup if the operator explicitly wants to. If normal PowerShell cannot delete them, suggest Administrator PowerShell. Do not let these warnings derail active engineering work.

## Parallel workstream rhythm

The operator approved parallel workstreams. It is acceptable to plan or open a documentation/architecture PR while another implementation PR is running CI, as long as the branches are cleanly separated and the user is told which one is active.

Current workstream categories:

- Collector Foundation
- Market Intelligence
- Business Operations
- Desktop Experience
- Jarvis Automation

Use parallel workstreams to avoid idle time, but do not merge conflicting branches blindly. If one branch depends on another, wait for the dependency to merge and then rebase or recreate from updated `main` when needed.

## MarketDEX build discipline

Keep changes narrow and authority-bound.

For each build, state:

- what changed;
- what did not change;
- whether CI is running, green, failed, or not started;
- whether the operator should pull;
- whether visual verification is required;
- whether ChatGPT Work is recommended.

Do not introduce speculative persistence, automation, mutation, or live-provider behavior unless it has been explicitly authorized by the relevant architecture gate.

## Market Intelligence current boundary

Build 700 is a provider-neutral, offline-first Market Intelligence foundation.

Current allowed direction:

- normalized observations;
- fixture-backed adapters;
- provider-neutral gateways;
- read-only attention and recommendation services;
- evidence-backed signals.

Current non-goals:

- live APIs;
- scraping;
- credentials;
- cloud sync;
- automated buy, sell, grade, list, restock, or reprice actions;
- direct mutation of Product Registry, Inventory, Collection, Portfolio, Listings, Reports, or Settlement.

## End-of-response checklist

Before ending a status response, include the applicable items:

- progress bar, if helpful;
- current PR and CI state;
- `Pull now` or `Do not pull yet`;
- `VISUAL CHECK REQUIRED` only when applicable;
- ChatGPT Work handoff note only when applicable;
- next step.
