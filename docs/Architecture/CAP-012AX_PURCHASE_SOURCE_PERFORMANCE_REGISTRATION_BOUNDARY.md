# CAP-012AX — Purchase Source Performance Registration and Live-Execution Boundary

## Status

Planning boundary for issue #699. This document does not register or execute the report.

## Authorized future slice

A later implementation may expose the already-composed `PurchaseSourcePerformanceProvider` through the existing composition-owned Reports query path. It must:

- use one canonical report identifier and definition owned by the existing `ReportCatalog`;
- route only validated Purchase Source Performance requests;
- preserve provider unavailable/conflicting outcomes without converting them to empty or zero evidence;
- retain composition ownership and constructor injection;
- leave the existing Inventory Age and Inventory Turnover report paths unchanged;
- prove deterministic request/result provenance and zero writes.

## Explicit gates

The implementation must remain UI-free and must not alter formulas, calculators, source authority, schema, persistence, or provider behavior. Presentation binding, charts, exports, rankings, recommendations, and live workspace execution require a separate reviewed boundary after registration tests are green.

## Required verification

Focused tests must prove canonical catalog identity, query routing to the composed provider, exact request preservation, fail-closed unavailable/conflicting propagation, deterministic provenance, and unchanged existing report routes.
