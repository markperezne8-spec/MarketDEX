# MarketDEX OS Startup Protocol

**Status:** Active  
**Authority:** Engineering governance  
**Owner:** Lead Software Architect  
**Update trigger:** Governance authority or canonical startup inputs change

## Purpose

Restore verified MarketDEX engineering context from version-controlled evidence at the beginning of every engineering session. Chat summaries and conversational memory are navigation aids only.

## Bootstrap Command

`Bootstrap MarketDEX`

When this command is received, do not begin with roadmap discussion or implementation assumptions. Perform the bootstrap gate below.

## Mandatory Bootstrap Gate

1. Inspect repository `main` and identify the permanent application entry point and current implementation structure.
2. Review current CI health and permanent verification gates.
3. Read this file.
4. Read `FoundationCheckpoint.md` as the single authoritative current-state and exact-resume document.
5. Read `CheckpointManifest.md` as the permanent historical checkpoint and synchronization index.
6. Read `CommunicationWorkingContract.md` as the full repository-backed collaboration, workflow, and Product Owner preference contract.
7. Read `docs/governance/Engineering_Protocol.md`.
8. Read `docs/governance/Communication_Protocol.md` and apply its compact Product Owner response contract for the session.
9. Read `docs/engineering/Capability_Matrix.md`.
10. Read `docs/engineering/Repository_Reconciliation.md`.
11. Read `docs/architecture/Desktop_Engineering_Charter.md` and `docs/architecture/Requirements_Traceability_Matrix.md`.
12. Review active issues, open pull requests, recent merged pull requests, and current branch activity.
13. Resume the active repository-backed delivery boundary from `FoundationCheckpoint.md` after reconciling it against `main`, accepted artifacts, merged history, CI, and the Capability Matrix.

Historical `docs/governance/EC-XXX_*.md` files may be consulted when a current authority explicitly references them or when historical engineering evidence is required. They are not the default current-state resume authority and must not override `FoundationCheckpoint.md`, `CheckpointManifest.md`, repository `main`, accepted artifacts, or merged verification evidence.

If a canonical document listed above does not yet exist, record that fact as a reconciliation gap. Do not invent its contents from chat memory.

## Mandatory Bootstrap Output Gate

The first material engineering progress response after `Bootstrap MarketDEX` must visibly render the Communication Protocol progress contract. It must include a labeled `MarketDEX Progress` bar, not only a percentage in prose.

Use a compact visual bar plus an explicit percentage, for example:

`MarketDEX Progress — [████████░░] 80%`

The percentage must be grounded in a named repository-backed scope or tracker. Never infer whole-project completion from chat memory. The same response must also include `NEXT STEP — JARVIS ACTION`, `MARK ACTION`, the pull instruction, and the app visual-check instruction required by `docs/governance/Communication_Protocol.md`.

This bootstrap output gate is repository authority. A new session must reconstruct and apply it from this protocol and the active Communication Protocol rather than relying on prior chat behavior.

## Low-Friction Session Rule

After bootstrap, default to execution rather than repeated process narration. Preserve mandatory gates, but batch same-family low-risk work under the Engineering Protocol speed policy. Ask the Product Owner to pull only at a meaningful checkpoint, before local or visual verification, or when the local baseline is required for the next action.

Every response that requires the Product Owner to act must include the exact command, full repository file name/path, or navigable GitHub destination needed for that action. Explicitly state whether the desktop app must be opened for a visual check.

## Authority Order

1. Repository `main` — implementation truth.
2. Accepted workbook artifact in `artifacts/calc/` — business specification truth.
3. Merged pull request history and CI/test evidence — delivered capability evidence.
4. `FoundationCheckpoint.md` — current-state and exact-resume authority derived from the authorities above.
5. `CheckpointManifest.md` — permanent historical checkpoint and synchronization index.
6. Capability Matrix — operational engineering status derived from the authorities above.
7. Chat context — collaboration context only.

When sources conflict, reconcile against higher authority before recommending or implementing work.

## Mandatory Pre-Build Classification

Before opening an implementation branch, search the permanent codebase and merged history for the proposed capability. Classify it as exactly one of:

- `Complete`
- `Partial`
- `Missing`
- `Deprecated`

Only `Partial` or `Missing` capabilities may create new implementation work. A `Complete` capability may receive a separately justified improvement or defect boundary; it must not be rebuilt.

## Duplicate Prevention Gate

Reject any change that creates a competing permanent implementation, including a second application root, second launcher authority, parallel database authority, duplicate canonical governance document, or overlapping capability tracker.

Prefer extension or consolidation over creation.

## Session Output Rule

After bootstrap, communicate only material conflicts, blockers, required Product Owner decisions, required Product Owner actions, meaningful checkpoints, or the active delivery result. Do not repeat established governance unless a repository conflict requires it.

## Standing Principle

**If the repository can answer the question, do not ask the conversation. Respect existing work.**
