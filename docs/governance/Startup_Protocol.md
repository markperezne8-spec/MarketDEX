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
4. Read `docs/governance/Project_Manifest.md`.
5. Read `docs/governance/Engineering_Protocol.md`.
6. Read the latest `docs/governance/EC-XXX_*.md` engineering checkpoint.
7. Read `docs/engineering/Capability_Matrix.md`.
8. Read `docs/engineering/Repository_Reconciliation.md`.
9. Review active issues, open pull requests, and recent merged pull requests.
10. Resume the active repository-backed delivery boundary.

If a canonical document listed above does not yet exist, record that fact as a reconciliation gap. Do not invent its contents from chat memory.

## Authority Order

1. Repository `main` — implementation truth.
2. Accepted workbook artifact in `artifacts/calc/` — business specification truth.
3. Merged pull request history and CI/test evidence — delivered capability evidence.
4. Capability Matrix — operational engineering status derived from the authorities above.
5. Chat context — collaboration context only.

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

After bootstrap, communicate only material conflicts, blockers, required Product Owner decisions, or the active delivery result. Do not repeat established governance unless a repository conflict requires it.

## Standing Principle

**If the repository can answer the question, do not ask the conversation. Respect existing work.**
