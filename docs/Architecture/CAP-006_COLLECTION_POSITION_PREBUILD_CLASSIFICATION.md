# CAP-006 — Collection Position Pre-Build Classification

**Status:** PLAN — pre-build classification only  
**Capability:** CAP-006 Collection  
**Requirement:** REQ-COL-001  
**Authority boundary:** Collection ownership truth, separate from business Inventory authority

## Purpose

Define the smallest safe Collection boundary before implementation begins. This document does not create Collection persistence, commands, services, or UI. It records the evidence that must be resolved before a Collection vertical slice can enter BUILD status.

## Repository evidence

- `docs/Architecture/Domain_Model.md` defines Collection Position as ownership truth for collector intent.
- `docs/Architecture/Modular_Collectibles_Platform_Blueprint.md` requires Collection Position, collection queries, and explicit ownership transitions.
- `docs/governance/Canonical_Product_Terminology.md` defines Collection as personally held items governed by collector intent and prohibits a competing Personal Collection workspace name.
- CAP-005 Product Registry is now complete for `REQ-PROD-001` and provides the catalog identity boundary Collection must reference.
- `artifacts/calc/MarketDEX_Calc_V0_M19_B1_Authoritative_Workbook_Specification_Freeze.ods`, sheet `❤️ Collection`, identifies `CALC V0 · BUILD 007` as a protected worksheet responsibility whose business interface is not yet implemented.
- No verified root Collection service, repository, schema authority, or dedicated regression suite exists on `main`.

## Classification

CAP-006 is **Missing** in the permanent runtime. The authoritative workbook currently provides only a protected Collection shell and explicitly prohibits speculative formulas, fake metrics, and architecture redesign. Existing `app/ui/` collection cards, navigation labels, and placeholders are presentation evidence only; they do not establish Collection ownership authority and must not be promoted by assumption.

## Required ownership boundary

Collection must own the collector-intent position of a product. Inventory must remain the business-intent position. A product may be represented in either or both contexts, but the two positions must not share a mutable status field or become one replacement database.

The first specification must resolve:

- stable Collection Position identity and its reference to canonical `product_id`;
- quantity, condition, grade, location, custody, acquisition evidence, and provenance fields required by the approved workbook responsibility;
- collector intent vocabulary, including goals, favorites, never-sell intent, and willingness to trade or sell, without inventing unapproved enum values;
- ownership lifecycle and history rules for acquire, adjust, transfer, archive, and intent changes;
- how a Collection Position relates to an Inventory Position without copying or mutating Inventory authority;
- whether cost and valuation are source evidence, a derived read model, or outside the first vertical slice;
- append-only event, audit, replay, restart, and zero-mutation requirements.

## Proposed first vertical slice

After the Collection worksheet responsibility is expanded and approved by Spreadsheet Design, the first implementation may be limited to:

1. a canonical Collection Position read model over one authoritative persistence boundary;
2. a read-only Collection Overview workspace using the existing workspace registry and design system;
3. deterministic empty, unmatched, restart, and zero-mutation behavior;
4. focused service, repository, workspace, navigation, and CI evidence;
5. explicit separation from Inventory, Product Registry, Portfolio, and Reports.

No write command or lifecycle transition should be implemented until the responsible business fields and evidence rules are design-locked.

## Non-goals

- no second catalog or Product Registry;
- no copy of Inventory tables as Collection tables without an approved ownership model;
- no Collection CRUD, schema migration, or UI implementation in this classification step;
- no Portfolio, Reports & Insights, valuation, grading, wishlist, or market-data expansion;
- no automatic conversion between Inventory Position and Collection Position;
- no external catalog API or cloud synchronization.

## Definition of Ready for BUILD

CAP-006 may advance from PLAN to BUILD only when the repository contains:

- approved workbook responsibility and field vocabulary;
- a written Collection Position and ownership-transition contract;
- command, query, event, repository, and persistence boundaries;
- migration, replay, restart, immutability, and rollback expectations;
- acceptance tests for authority separation and zero mutation;
- a clear first workspace acceptance path and CI gate;
- an updated Capability Matrix and Requirements Traceability Matrix.

## Next gate

Return this classification to Spreadsheet Design authority for the Collection Position responsibility. Do not implement Collection code from roadmap language or placeholder UI evidence alone.
