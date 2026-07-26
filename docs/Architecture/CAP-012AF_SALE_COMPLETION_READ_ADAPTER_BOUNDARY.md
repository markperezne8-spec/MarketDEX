# CAP-012AF Sale-Completion Read-Adapter Boundary

## Status

Approved planning boundary only. This document authorizes no schema, migration, write path, or application composition.

## Responsibility

A future concrete adapter may implement `SaleCompletionRepository` by reading sale-completion evidence from one explicitly identified durable source and passing the retrieved evidence through `build_sale_completion_repository_read` without weakening coverage or validation semantics.

## Required adapter behavior

- translate `SaleCompletionQuery` into source-native read criteria without widening identity scope;
- preserve explicit inventory IDs, sale IDs, `as_of`, and optional completion-range boundaries;
- determine coverage explicitly rather than inferring completeness from returned row count;
- map each source row into `SaleCompletionEvidence` without descriptive or proximity-based identity inference;
- retain duplicate and conflicting rows for CAP-012AC validation rather than silently deduplicating them;
- fail closed on malformed rows, partial reads, decode failures, source errors, unknown coverage, and unsupported source values;
- pass valid decoded evidence to `build_sale_completion_repository_read` for canonical ordering and typed result construction;
- remain read-only and synchronous at this boundary.

## Coverage determination

Complete coverage may be reported only when the adapter can establish that the durable source was fully queried for the exact requested scope and boundary. An empty result is available only when that complete coverage is established.

Unknown, interrupted, stale, partially synchronized, or otherwise unverifiable coverage must return unavailable. Decode or validation conflicts must remain conflicts and must not be converted to unavailable or empty available output.

## Row mapping

The adapter must map source values directly into the domain fields required by `SaleCompletionEvidence`:

- sale-completion evidence identity;
- sale identity;
- inventory identity;
- lifecycle state;
- source system;
- recorded timestamp;
- lineage parent identity when present;
- completed quantity and completion timestamp when authorized by lifecycle state.

Unsupported lifecycle values, invalid timestamps, missing required identities, invalid quantities, or inconsistent nullable fields must fail closed with stable adapter diagnostics.

## Determinism

Source ordering is not trusted. The adapter may return rows in any source-native order, but the repository result must use CAP-012AC canonical ordering. No adapter-specific ranking or preferred-source ordering is authorized.

## Explicitly unauthorized

- schema creation, schema modification, or migrations;
- insert, append, update, delete, repair, reconciliation, or mutation APIs;
- combining multiple durable sources;
- application services, providers, dependency registration, or runtime composition;
- imports, marketplace APIs, networking, polling, reports, previews, exports, or UI;
- settlement, revenue, cost, margin, ranking, recommendation, or trend metrics;
- inferred identity, fuzzy matching, or descriptive joins.

## Next gate

The next controlled build may implement one read-only adapter against an already-existing repository-supported durable source, plus adapter diagnostics and isolated contract tests. Any schema work, write path, multi-source composition, or application registration requires a separate reviewed boundary.
