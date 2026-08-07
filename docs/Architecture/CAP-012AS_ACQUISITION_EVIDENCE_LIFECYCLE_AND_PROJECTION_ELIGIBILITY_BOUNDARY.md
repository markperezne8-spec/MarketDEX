# CAP-012AS — Acquisition Evidence Lifecycle and Projection Eligibility Boundary

## Status and scope

This is the architecture boundary for issue #689. It defines how immutable CAP-012AR acquisition-evidence rows may be considered for a future read-only projection. It authorizes no schema, persistence, service, repository, reader, provider, adapter, composition, report, calculation, or UI implementation.

## Distinct grains

CAP-012AR stores acquisition-evidence rows. One Inventory asset may have more than one row over time. The existing InventoryAcquisitionProjectionRecord contract permits exactly one record per canonical inventory_id. A future reader must not aggregate repeated acquisitions or select a row by convenience. It returns a projection record only when one eligible evidence row can be established without ambiguity.

## Eligibility at as_of

Eligibility is determined from immutable recorded_at and supersedes_acquisition_evidence_id. A row is eligible when it was recorded no later than the request as_of, has no eligible successor at that as_of, and all declared acquisition fields remain valid. A successor becomes eligible only at its own recorded_at. Future-dated evidence is invisible to an earlier as_of.

The evidence service currently proves that a declared predecessor exists. Before any reader implementation, the read boundary must also validate that predecessor and successor share the same canonical asset identity. A cross-asset link is conflicting, never a correction.

## Fail-closed projection resolution

For each canonical asset, a future reader must return unavailable or conflicting with no projection records when it observes:

- no eligible evidence, missing provenance, or partial coverage;
- dangling or cross-asset supersession;
- more than one eligible successor, a branching chain, a cycle, or impossible ordering;
- multiple eligible acquisition rows for one asset; or
- duplicate canonical inventory identity, malformed date/source/quantity, out-of-period evidence, or evidence later than as_of.

Repeated acquisitions are not summed. A later contract may define a different projection grain only through a separately approved boundary.

## Determinism and provenance

An available result preserves the exact selected evidence identity, its immutable provenance reference, and the lifecycle chain used for eligibility. Results retain the projection contract order: acquisition date, canonical inventory identity, case-folded source label, then exact source label. Empty complete coverage may be available; partial coverage is never silently dropped.

## Next controlled movement

A future implementation issue may add a read-only lifecycle validator and canonical acquisition-evidence reader only after this boundary is merged. It must validate all rules above before returning the existing immutable projection result. It must not compose the Purchase Source Performance provider or change reports, catalog registration, or UI.