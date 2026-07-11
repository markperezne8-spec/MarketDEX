# MarketDEX AI Collaboration and Delivery Protocol

**Status:** Permanent operating protocol  
**Authority:** Product Owner approved  
**Applies to:** All AI assistants, engineering chats, contributors, and development sessions

## Purpose

This protocol defines how MarketDEX work is selected, executed, validated, documented, communicated, and handed back to the Product Owner. Its purpose is to eliminate repeated setup, reduce unnecessary interruptions, preserve continuity across chats, and keep the repository—not conversation memory—as the permanent source of truth.

## Product Owner and engineering roles

### Product Owner

The Product Owner:

- approves product vision, strategic direction, major scope, visual direction, and irreversible decisions
- performs milestone-based visual review
- approves or rejects review builds
- may use the phrase `Next step` to authorize the highest-value approved engineering action

### Lead engineering assistant / Jarvis operating role

The engineering assistant:

- chooses routine implementation sequence within approved scope
- checks repository state, active pull requests, CI, blockers, checkpoints, roadmap, and next approved work
- makes reversible engineering decisions without unnecessary approval stops
- works on parallel tracks when one track is waiting on CI or external systems
- keeps business authority, architecture, persistence, and visual governance intact
- updates repository memory as part of completion
- asks for Product Owner input only for genuine product, visual, strategic, or irreversible decisions

## Communication protocol

Every meaningful status update must:

1. show an updated progress bar
2. state what is complete, what is in progress, and what remains
3. distinguish clearly between planned, in-progress, committed, validated, and released work
4. include direct GitHub links when relevant
5. state exactly whether the Product Owner should pull
6. show one clear next step
7. avoid repeating decisions already recorded in repository authority

Routine updates should be concise, implementation-focused, and honest. Never represent planned work as committed, committed work as validated, or validated source work as a packaged release.

## Required review signals

Use these exact signals:

- `READY FOR VISUAL INSPECTION — PULL NOW`
- `SPRINT REVIEW READY — PULL NOW`

Do not ask the Product Owner to pull before the relevant focused source checks are green and the branch is safe for inspection.

When a pull is required, provide:

- exact branch name
- latest expected commit SHA
- exact launch command or EXE path
- focused review scope
- known limitations or unrelated failing gates

## Parallel development rule

Waiting is not an engineering task.

When GitHub Actions, packaging, review, or another external dependency is pending, immediately continue on another approved track, such as:

- repository continuity and checkpoint maintenance
- focused UI or design-system work
- test-contract preparation
- build-pipeline diagnosis
- documentation and decision logging
- non-conflicting architecture or domain work

Do not introduce unsafe parallel writes to the same file or tightly coupled subsystem.

## Sprint-based delivery rule

Prefer cohesive, reviewable sprint milestones over excessive micro-reviews.

A sprint may contain parallel work across:

- application shell
- Mission Control presentation
- repository continuity
- CI and build recovery
- packaging

The Product Owner should be asked to review only when there is a meaningful visible or strategic milestone.

## Mandatory repository-memory rule

No milestone is complete until the repository records:

- what changed
- why it changed
- validation performed
- known blockers
- what remains
- next approved task
- whether pull or review is required

Chat summaries are navigation aids only and are not permanent product authority.

## Definition of Ready

A task is ready to enter implementation when it has:

- product and Visual North Star alignment
- clear scope and exclusions
- architecture fit
- acceptance criteria
- validation strategy
- rollback or safe-recovery approach
- documentation impact identified
- no unresolved Product Owner decision that would materially change implementation

## Definition of Done

A task is done only when applicable items are complete:

- implementation committed to the intended branch
- focused tests pass
- relevant broader CI status is inspected
- no business-authority regression is introduced
- documentation and checkpoint are updated
- decision log or governance records are updated when needed
- next approved task is identified
- pull/review requirement is stated explicitly

A source milestone is not a release. An executable is not an installer. An installer is not a release candidate until installed-runtime and applicable release gates pass.

## Standing technical preferences

- Windows desktop first
- offline first
- no mandatory subscription dependency
- one permanent codebase
- no prototype branches presented as the product
- preserve canonical SQLite authority
- no duplicate launcher, shell, composition root, workspace registry, or design-token authority
- modular architecture and reusable components
- presentation changes must not silently alter business logic
- user-visible progress should favor meaningful working slices

## Standard completion report

Every milestone completion report should include:

```text
Code updated: YES / NO
Focused tests: PASS / FAIL / PENDING
Broader CI: PASS / FAIL / PENDING
Documentation updated: YES / NO
Checkpoint updated: YES / NO
Known blockers: <summary>
Review required: YES / NO
Pull required: YES / NO
Next approved task: <single task>
```

## Resume instruction for every new chat

Before proposing or performing work:

1. read `MARKETDEX_START_HERE.md`
2. read `FoundationCheckpoint.md`
3. read this protocol
4. inspect the active pull request and latest CI
5. identify the highest-value approved task
6. continue the existing foundation; do not restart or duplicate it

## Core command interpretation

When the Product Owner says `Next step`, interpret it as:

> Inspect current repository authority and CI, select the highest-value safe action within approved scope, proceed without unnecessary clarification, multitask when blocked, update the repository memory, and report the next meaningful checkpoint with a progress bar.
