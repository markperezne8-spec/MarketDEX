# CAP-012BE - Purchase Source Performance Composition Snapshot Boundary

## Status

Planning boundary for issue #713. This document authorizes a future composition-owned snapshot implementation only after the Reports workspace visual preview is accepted and merged.

## Purpose

The Reports workspace can present Purchase Source Performance only from an immutable presentation snapshot. A later implementation may let `ApplicationComposition` build that snapshot and inject it into `ReportsWorkspace`, but the workspace must remain a read-only presenter.

## Existing authority

Current main already contains these relevant boundaries:

- `reports.purchase_source_performance_query.PurchaseSourcePerformanceQueryService` owns the approved report query path.
- `reports.purchase_source_performance_presentation.present_purchase_source_performance` maps query responses into immutable presentation rows.
- `composition.application_composition.ApplicationComposition` owns runtime construction and report service wiring.
- `ui.reports_workspace.ReportsWorkspace` presents Reports surfaces and must not construct providers, repositories, or SQLite dependencies.

## Required future implementation contract

A later implementation may add a composition-owned Purchase Source Performance snapshot if it obeys all of these rules:

- build the snapshot in `ApplicationComposition` or a composition-owned helper;
- use only the existing Reports query service and presentation mapper;
- pass an immutable `PurchaseSourcePerformancePresentation` into `ReportsWorkspace` by constructor injection;
- preserve request period, as-of date, source coverage, provenance, source labels, outcomes, and deterministic row order;
- keep unavailable and conflicting evidence visible as unavailable/conflicting presentation states;
- never convert missing, unavailable, or conflicting evidence to zero values;
- keep the workspace read-only and presentation-only;
- leave Inventory Age and Inventory Turnover behavior unchanged.

## Snapshot request policy

The snapshot request must be explicit and deterministic. A later code PR must document or test:

- the selected report id;
- the request period and as-of date;
- the source domains used by the query path;
- the provenance emitted into the presentation;
- the unavailable fallback used when no safe snapshot can be prepared.

A placeholder or preview snapshot is acceptable only when it is clearly labeled unavailable and does not claim live evidence.

## Fail-closed cases

The future implementation must emit an unavailable or conflicting presentation, not partial success, when any of these conditions occur:

- the query path is unavailable;
- source coverage is incomplete or contradictory;
- provenance is missing;
- the response cannot be mapped deterministically;
- a provider exception or dependency failure occurs;
- the request period or as-of context is ambiguous.

## Explicit non-goals

This boundary authorizes no runtime implementation, UI styling, tests, provider execution changes, new query type, schema, persistence, mutation authority, automation, charts, exports, ranking, recommendation, or changes to PR #710.

## Verification for a later code PR

A later implementation must include focused tests proving:

- constructor injection is used;
- the workspace does not construct providers, repositories, SQLite objects, or report services;
- unavailable/conflicting states remain visible;
- zero values remain distinct from unavailable values;
- source coverage and provenance are preserved;
- no writes, persistence changes, or mutation authority are introduced.

## Merge dependency

The implementation authorized by this planning boundary should wait until the Reports workspace visual preview PR has passed visual acceptance and merged. This document may merge independently because it is documentation-only and does not alter application behavior.
