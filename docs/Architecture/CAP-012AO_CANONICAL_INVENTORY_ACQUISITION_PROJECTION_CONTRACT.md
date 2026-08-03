# CAP-012AO — Canonical Inventory Acquisition Projection Contract

## Status

Implemented as a runtime-neutral, immutable contract boundary. This slice does not authorize or implement a repository query, SQL, schema, persistence, adapter, application composition, report registration, or UI.

## Delivered boundary

`core/inventory_acquisition_projection.py` defines:

- a timezone-aware inclusive `as_of` request over an inclusive-start/exclusive-end date period;
- immutable canonical acquisition records containing Inventory identity, authoritative acquired units, acquisition date, and exact trimmed purchase-source label;
- exact complete coverage tied to the request boundaries;
- available, unavailable, and conflicting outcomes;
- stable diagnostics carrying a reason code, message, and affected canonical identities;
- deterministic record ordering by acquisition date, canonical identity, case-folded label, and exact label;
- fail-closed validation for blank identity/label, non-positive quantity, malformed dates, duplicate identity, coverage mismatch, out-of-period evidence, evidence after `as_of`, and missing provenance.

## Authority preservation

The contract deliberately does not derive acquired units from current `inventory_authority.quantity`, does not promote mutable `inventory_business_details` metadata into acquisition authority, and does not depend on SQLite or a concrete repository. CAP-012AN remains the authority for why those existing fields cannot safely satisfy this projection on their own.

## Verification

`tests/test_cap012ao_inventory_acquisition_projection_contract.py` covers valid and empty complete results, deterministic ordering, exact-label preservation, invalid quantity/date/label, request boundaries, duplicate identity, coverage mismatch, period and `as_of` enforcement, unavailable/conflicting diagnostics, immutability, and absence of SQLite/repository dependencies.

## Next boundary

The next separately approved slice may define a read-only canonical projection provider that obtains authoritative acquisition evidence and returns this contract. It must fail closed when the repository cannot establish acquired units, acquisition date, purchase source, or complete coverage. The Purchase Source Performance adapter and runtime composition remain unauthorized until that projection provider is proven.
