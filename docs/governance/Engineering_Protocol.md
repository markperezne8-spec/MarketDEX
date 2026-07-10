# MarketDEX OS Engineering Protocol

**Status:** Active
**Authority:** Engineering governance
**Owner:** Lead Software Architect
**Update trigger:** Accepted engineering process change

## Purpose

Define the mandatory engineering lifecycle for the single permanent MarketDEX OS codebase.

## Rule Zero

Respect existing work. Before creating anything, prove what already exists from repository evidence. Extend or consolidate existing work before creating a new implementation or document.

## Authorities

- `artifacts/calc/` defines authoritative workbook business behavior.
- Repository `main` defines accepted implementation reality.
- CI and tests provide verification evidence.
- `docs/engineering/Capability_Matrix.md` records derived operational status.
- Chat context does not define project state.

## Definition of Ready

A delivery boundary is Ready only when the Startup Protocol has been performed; current `main`, CI, active work, and recent merged work have been inspected; authority is identified; existing implementation has been searched; capability status is classified; the smallest safe mergeable boundary is defined; and duplicate implementation risk has been rejected.

## Delivery Lifecycle

1. Bootstrap and perform the repository reality check.
2. Reconcile capability evidence.
3. Select one controlled delivery boundary.
4. Create one branch for that boundary.
5. Implement through the existing permanent architecture.
6. Add or update verification evidence.
7. Open one pull request.
8. Verify CI and regression compatibility.
9. Merge only when the boundary is safe and releasable.
10. Update the Capability Matrix when implementation status changes.
11. Close the boundary and repeat.

## Definition of Done

A boundary is Complete only when authority and traceability are identified, required implementation layers are complete, regression evidence exists, CI is healthy, no competing permanent architecture or duplicate canonical artifact was introduced, `main` remains releasable, and durable engineering memory is updated when affected.

## Permanent Codebase Rule

MarketDEX OS has one permanent application codebase. Do not create a competing application root, duplicate launcher authority, or parallel database authority.

## Repository Hygiene

- One concept has one canonical document.
- One canonical document has one canonical location.
- Search before creating.
- Consolidate rather than proliferate.
- Use existing repository naming patterns unless a deliberate migration is approved.
- Governance exists to enable delivery, not replace it.

## Roles

The Product Owner owns business vision, priority, acceptance, and final product judgment. The Lead Software Architect owns repository reconciliation, architecture, delivery boundaries, traceability, technical review, and regression protection. Coding assistants may accelerate implementation but do not define architecture or business authority. CI is the automated verification gate before merge.

## Speed Policy

Optimize for the smallest safe mergeable improvement. Encode approved decisions and move to implementation instead of repeatedly redescribing them.
