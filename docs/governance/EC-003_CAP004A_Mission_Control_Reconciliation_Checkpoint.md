# EC-003 — CAP-004A Mission Control Reconciliation Checkpoint

**Status:** Active checkpoint  
**Date:** 2026-07-10  
**Authority:** Engineering continuity  
**Repository:** `markperezne8-spec/MarketDEX`

## Purpose

Preserve the repository-backed Mission Control authority decision so future sessions do not reopen or redesign the dashboard from chat memory.

## Audit Result

The permanent root runtime already has a complete Mission Control vertical slice:

- root `launcher.py` constructs `MissionControlService` from the canonical runtime SQLite path;
- root `launcher.py` injects that service into root `ui/main_window.py`;
- root `MainWindow` renders and refreshes the Mission Control card contract from `MissionControlService.snapshot()`;
- `MissionControlService` is read-only and projects protected SQLite authority;
- the dedicated Mission Control vertical-slice CI gate runs `tests/test_mission_control_integration.py`.

A broader `DashboardService` also exists, but it is not selected by the permanent root launcher. Its metric names and source tables differ from the permanent root Mission Control contract. It must not be silently promoted or merged into Mission Control by assumption.

## Canonical Projection Decision

`services/mission_control_service.py` is the canonical permanent desktop Mission Control projection selected by root `launcher.py`.

The canonical snapshot contract is exactly:

- `inventory_units`
- `inventory_asset_count`
- `inventory_cost_minor`
- `completed_sales`
- `revenue_minor`
- `profit_minor`
- `verified_audits`
- `authority_events`
- `database_path`

## Controlled Repair

No application-code integration repair was justified. The permanent runtime already selected one canonical path. CAP-004A therefore adds focused regression evidence that locks the exact snapshot contract and permanent-root launcher selection, then reconciles derived capability and traceability status.

## Classification

CAP-004 — Mission Control / dashboard is `Complete` for the current REQ-MIS-001 desktop authority boundary.

Do not rebuild Mission Control. Do not promote `DashboardService`, add charts, or introduce broader metrics without a separately justified workbook or repository-backed capability boundary.

## Resume Boundary

The next controlled action is repository-backed capability selection among CAP-005 Product Registry (`Partial`), CAP-006 Collection (`Missing`), and CAP-012 Reports (`Missing`). Apply the mandatory pre-build classification gate before implementation.