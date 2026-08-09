# CAP-012AZ — Purchase Source Performance Presentation Boundary

## Status

Planning boundary for issue #703. This document authorizes a future read-only presentation slice only.

## Required presentation contract

A later implementation may map the existing `PurchaseSourcePerformanceQueryResponse` into a Reports workspace view model. It must:

- preserve exact source labels and deterministic ordering;
- show valid, zero-sell-through, unavailable, and conflicting outcomes distinctly;
- never replace unavailable/conflicting evidence with zeroes or empty success;
- retain source domains, coverage, provenance, request period, and as-of context;
- use the existing composition-owned query path and avoid direct SQLite/repository access;
- leave Inventory Age and Inventory Turnover presentation unchanged.

## Explicit non-goals

No provider, calculator, schema, persistence, report catalog, chart, export, ranking, recommendation, or mutation changes are authorized. Live workspace execution requires a separate implementation boundary after focused view-model tests are green.

## Verification

Focused tests must prove deterministic mapping, outcome visibility, provenance preservation, stable ordering, and zero-write behavior.
