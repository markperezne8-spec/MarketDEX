# CAP-006 Collection — Position Authority Boundary

**Status:** Planning-only boundary  
**Capability:** CAP-006 Collection  
**Issue:** #723

## Purpose

Define the authority questions that must be resolved before the Partial Collection Position surface can expand beyond its current read-only projection.

This document does not authorize persistence or mutation. It records the contract questions for a future workbook-backed decision.

## Current repository authority

The existing read-only boundary is preserved:

- `services/collection_position_service.py` provides the current Collection Position projection.
- `ui/collection_position_workspace.py` presents the projection without becoming a second authority.
- `docs/Architecture/CAP-006_COLLECTION_POSITION_PREBUILD_CLASSIFICATION.md` records the pre-build classification.
- `docs/Architecture/CAP-006B_COLLECTION_WRITE_AUTHORITY_GATE.md` protects the current no-write boundary.
- `docs/Architecture/CAP-006_COLLECTION_BUSINESS_RESPONSIBILITY_INTAKE.md` records the business-responsibility intake surface.
- `composition/application_composition.py` remains the application composition root.

## Required future authority decisions

Before any Collection expansion is authorized, a separately reviewed workbook-backed contract must define:

1. the canonical position grain and field vocabulary;
2. canonical Product Registry and Inventory identity linkage;
3. evidence ownership for quantity, location, acquisition, condition, grade, collector intent, valuation, and lifecycle facts;
4. lifecycle, transition, archive, and reconciliation semantics;
5. read-only projection versus future write-authority responsibilities;
6. missing, partial, contradictory, stale, and unsupported evidence outcomes;
7. rules preventing inference of condition, grade, valuation, collector intent, or ownership transitions from unrelated fields.

## Explicit non-goals

This planning boundary does not authorize Collection schema, persistence, migration, CRUD, mutation, automatic Inventory conversion, valuation, grading, collector-intent inference, UI changes, or business-state mutation.

The current read-only Collection Position projection remains the only approved Collection surface.

## Decision

CAP-006 remains `Partial`. Any future implementation requires a separate approved issue after the workbook-backed position authority contract is reviewed and CI evidence is complete.

## Verification

Documentation-only CI with repository-path and symbol citation coverage. No visual check is required.
