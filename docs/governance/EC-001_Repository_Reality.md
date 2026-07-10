# EC-001 — Repository Reality

**Status:** Accepted
**Effective date:** 2026-07-10
**Authority:** Engineering checkpoint
**Owner:** Lead Software Architect
**Update trigger:** Frozen checkpoint; supersede with a later EC rather than rewriting the lesson

## Event

During the transition from workbook engineering to desktop engineering, a planning summary was treated as if it represented current implementation state. A new nested `desktop/` application foundation was proposed and implemented on a branch even though the repository already contained the permanent root desktop application and substantial Inventory, Pricing, Listing, database, UI, and test progress.

PR #118 was closed without merge after repository and CI evidence exposed the duplication risk. A duplicate connector-created PR #119 was also closed without merge.

## Root Cause

Conversation context and planning assumptions were allowed to precede repository reconciliation. The permanent codebase, merged history, and verification evidence were not inspected before implementation began.

## Corrective Action

Repository `main` is implementation truth. The accepted workbook in `artifacts/calc/` is business specification truth. Merged PR history and CI/test evidence prove delivered capability. Chat context is advisory only.

## Preventive Controls

1. Every engineering session begins with `docs/governance/Startup_Protocol.md`.
2. Every implementation boundary must satisfy the Definition of Ready in `docs/governance/Engineering_Protocol.md`.
3. Existing capabilities are classified before implementation.
4. Complete capabilities are not rebuilt.
5. A second application root, duplicate launcher authority, parallel database authority, or competing permanent architecture is rejected.
6. Canonical documents are searched before new governance artifacts are created.
7. Capability status is derived from repository and workbook evidence, not memory.

## Learned Principle

**If the repository can answer the question, do not ask the conversation. Respect existing work.**

## Process Change

MarketDEX OS moves from build-count-driven planning to capability-driven product engineering. The engineering loop is repository reality check, capability reconciliation, one controlled delivery boundary, implementation, verification, merge, and capability status update.

## Team Boundary

The Product Owner owns business vision and acceptance. The Lead Software Architect owns architecture, reconciliation, traceability, and delivery boundaries. Coding assistants accelerate implementation only. CI verifies merge safety.

## Naming and Repository Hygiene

Use one canonical name and location per durable concept. Extend or consolidate existing artifacts before creating new ones. Do not create overlapping trackers or parallel architecture documents.

## Checkpoint Result

This incident is considered resolved without merging the competing nested application. The lesson is now institutionalized as version-controlled engineering memory.
