# Build 701E — Inventory Age Report Projection Boundary

**Status:** PREBUILD CLASSIFICATION ONLY  
**Capability:** CAP-012 Reports  
**Depends on:** Build 701D Inventory Age Patterns definition fixture  
**Issue:** #250

## Decision

The first future Reports projection may answer:

> **What patterns does inventory age reveal?**

Build 701E defines the boundary only. It adds no runtime report row, query service, calculation, threshold, report execution, or user interface.

## Source authority

Inventory remains the sole source domain for this projection.

A future Reports query service may consume an approved Inventory read contract. It must not:

- open SQLite directly;
- call an Inventory repository from presentation code;
- copy Inventory tables into Reports storage;
- create or modify inventory positions;
- infer Listing, Settlement, Pricing, Collection, or Market Intelligence facts;
- redefine Inventory age or lifecycle authority.

Reports owns only an immutable presentation read model derived from approved Inventory evidence.

## Candidate immutable row vocabulary

A later explicitly approved implementation may define an immutable row containing:

- canonical inventory position identifier;
- canonical product identifier;
- human-readable product name supplied by an approved Inventory projection;
- acquisition or received date when authoritative evidence exists;
- age in whole days as of an explicit date;
- current quantity;
- current inventory status;
- storage location when approved for reporting;
- evidence availability state;
- source domain identifier;
- as-of date.

Every field remains read-only.

No monetary value, market price, profit, listing readiness, settlement status, collection intent, or recommendation belongs in this first row.

## Time and age meaning

A future age calculation must:

1. use an explicit as-of date;
2. use an authoritative Inventory start date defined by the Inventory contract;
3. calculate whole elapsed calendar days deterministically;
4. reject an as-of date earlier than the authoritative start date;
5. distinguish missing start-date evidence from an age of zero;
6. avoid wall-clock-dependent test behavior;
7. expose calculation meaning in the query contract.

Build 701E does not approve the exact Inventory start-date field. That selection requires evidence from the existing Inventory service contract before runtime implementation.

## Evidence availability

The projection must distinguish:

- **available** — authoritative start-date evidence exists and age can be derived;
- **unavailable** — required evidence is absent;
- **invalid** — source evidence is contradictory or the as-of date is earlier than the source date.

Unavailable is not zero. Invalid evidence must fail closed and remain visible for review.

## Deterministic ordering

A future result must use explicit stable ordering. The initial candidate order is:

1. unavailable or invalid evidence first for operator review;
2. available rows by age descending;
3. product name case-insensitively;
4. inventory position identifier.

The implementation build must lock this order through focused tests.

## Query boundary

A future service must be composition-owned and accept:

- an approved Inventory read dependency;
- an explicit as-of date.

It may return an immutable tuple of report rows. It must expose no save, update, delete, export, refresh-provider, schedule, or execute-business-command behavior.

Presentation must depend on the query service and immutable rows. It must not reproduce age calculations.

## First implementation gate

After Build 701E merges, Build 701F may introduce:

- an immutable `InventoryAgeReportRow`;
- controlled evidence-availability values;
- a pure deterministic age derivation function;
- focused tests using explicit dates.

Build 701F must remain persistence-free, composition-free, UI-free, export-free, and Inventory-read-contract independent. Application service wiring requires a later build after the Inventory start-date authority is proven.

## Non-goals

Build 701E introduces no:

- runtime report rows or services;
- Inventory query integration;
- exact Inventory start-date authority;
- calculations or thresholds;
- charts, exports, workspace, or navigation;
- schema, migrations, persistence, writes, imports, or caches;
- live providers, network calls, schedulers, alerts, cloud sync, or automation;
- business-domain mutation authority.
