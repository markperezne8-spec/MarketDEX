# EC-004 — CAP-005A Product Registry Authority Checkpoint

**Status:** Active checkpoint  
**Date:** 2026-07-10  
**Authority:** Engineering continuity  
**Repository:** `markperezne8-spec/MarketDEX`

## Purpose

Preserve the repository-backed Product Registry persistence reconciliation so future sessions do not recreate a private Product Registry database architecture from chat memory.

## Classification

CAP-005 is `Partial`, not Missing. `ProductRegistryService` already contained registration, canonical identity normalization, alias authority, duplicate/collision blocking, audit evidence, replay behavior, and restart verification.

## Proven Gap

The legacy service privately created Product Registry tables and incompatible copies of shared event, replay, and audit tables. Canonical `core/schema.py` did not own Product Registry persistence. Root runtime database authority therefore could not safely claim Product Registry persistence.

## Controlled Repair

CAP-005A:

- adds Product Registry tables and append-only history triggers to canonical schema version 24;
- makes `ProductRegistryService` initialize and transact through `DatabaseManager`;
- uses canonical `event_identity` and `audit_events` column contracts;
- reconstructs accepted replay identity from immutable event authority plus Product Registry authority rows;
- adds focused canonical-schema, restart, replay, duplicate, alias-collision, audit, and append-only regression evidence;
- adds the CAP-005A regression suite to Core Tests CI.

## Boundary

No Product Registry operator UI is introduced. No catalog import, external API, Collection, or Reports work is included.

## Resume Boundary

After CAP-005A CI and merge, reclassify CAP-005. Persistence authority may be Complete while operator workflow remains Partial. Select the next smallest proven Product Registry gap through repository evidence; do not assume UI requirements beyond REQ-PROD-001 authority.