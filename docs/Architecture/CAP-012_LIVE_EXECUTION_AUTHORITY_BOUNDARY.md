# CAP-012 Reports — Live Execution Authority Boundary

**Status:** Planning-only boundary  
**Capability:** CAP-012 Reports  
**Issue:** #722

## Purpose

Define the authority questions that must be resolved before Purchase Source Performance can move beyond the delivered read-only projection, adapter, and composition-owned snapshot.

This document does not authorize implementation. It is the review boundary for a future live-execution decision.

## Current repository authority

The existing read-only chain is preserved:

- `reports/purchase_source_performance_provider.py` owns the constructor-injected orchestration provider and fail-closed report outcomes.
- `reports/purchase_source_performance_inventory_adapter.py` exposes the delivered `PurchaseSourcePerformanceInventoryAdapter`.
- `core/inventory_acquisition_projection.py` and `core/sqlite_inventory_acquisition_projection_repository.py` expose the canonical acquisition projection authority.
- `core/sale_completion.py` and `services/sale_completion_query_service.py` remain the existing sale-completion evidence path.
- `composition/application_composition.py` remains the composition root.
- `ui/reports_workspace.py` remains a read-only presenter.

## Required future authority decisions

Before any live execution is authorized, a separately reviewed contract must define:

1. the exact source authority for completed-sale evidence and acquired-inventory identity linkage;
2. request-period, inclusive as-of, coverage, lifecycle, supersession, reversal, and provenance semantics;
3. deterministic available, unavailable, non-found, and conflicting outcomes;
4. duplicate, partial, malformed, contradictory, and unsupported evidence handling;
5. zero-inference rules that prohibit text, price, timing, settlement, or allocation coincidence as identity linkage;
6. the exact boundary between provider execution, application composition, presentation, and any later UI behavior;
7. read-only and zero-write guarantees.

## Explicit non-goals

This planning boundary does not authorize provider implementation, SQL, schema, persistence, migration, new queries, calculations, exports, networking, polling, automation, UI behavior, or business-state mutation.

The delivered Purchase Source Performance preview remains read-only and explicitly unavailable when a composition snapshot is not supplied.

## Decision

CAP-012 remains `Partial`. Any future live execution requires a separate approved implementation issue after this authority contract is reviewed and CI evidence is complete.

## Verification

Documentation-only CI with repository-path and symbol citation coverage. No visual check is required.
