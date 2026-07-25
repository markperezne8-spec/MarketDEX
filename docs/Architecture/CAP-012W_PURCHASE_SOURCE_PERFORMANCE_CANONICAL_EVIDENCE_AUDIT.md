# CAP-012W Purchase Source Performance Canonical Evidence Audit

## Status

Repository-search checkpoint after CAP-012V. Provider implementation remains blocked unless every required field and linkage is backed by a permanent read-only authority.

## Search result

Repository search confirms existing Purchase Source Performance contracts, calculator, and query boundary under `reports/`, plus purchase-source fields in Inventory-related models, schema, migrations, repositories, and services.

Search did not surface a clearly canonical confirmed-sale-completion read model that exposes all of the following together:

- completed unit quantity;
- completion date;
- stable linkage to the exact acquired inventory identity;
- authoritative handling of partial, duplicate, superseded, or contradictory completion evidence.

Terms such as `completed_sale_units` currently appear primarily in report contracts, calculators, previews, tests, dashboard projections, and planning documents. Those surfaces do not independently establish canonical sale-completion evidence authority.

## Acquisition evidence

Candidate acquisition authority exists in the permanent Inventory path, including purchase-source fields represented in:

- `app/models/asset.py`;
- `app/database/schema.py`;
- `app/database/migrations.py`;
- `app/repositories/asset_repository.py`;
- `services/inventory_app_service.py`.

A future provider must still verify the exact permanent field names and semantics for acquired units, acquisition date, stable inventory identity, and original trim-only purchase-source label before consuming them.

## Sale-completion evidence gap

No provider may infer completed-sale linkage from product names, SKUs, marketplace labels, listing text, source aliases, prices, or temporal proximity. Until a permanent sale-completion read path proves exact inventory identity linkage and authoritative completed-unit/date semantics, the provider cannot produce valid grouped evidence.

The existing Purchase Source Performance query boundary must therefore continue to return its approved unavailable or conflict semantics rather than treating missing completion evidence as zero.

## Decision

CAP-012W does **not** authorize provider implementation.

The next controlled build must identify or establish a separately approved canonical read-only sale-completion evidence boundary with stable inventory identity linkage. It must not add report provider code, registration, composition, UI, persistence, or mutation by assumption.

## Explicitly unauthorized

- Purchase Source Performance provider implementation;
- SQLite report adapter or ad hoc cross-domain query;
- report registration, application composition, or live execution;
- UI, chart, export, preview, or presenter work;
- schema changes, new persistence, caches, snapshots, or materialized views;
- text-based linkage, source aliasing, fuzzy matching, ranking, recommendation, or financial metrics;
- networking, polling, marketplace API access, or writes.

## Next gate

Create a planning-first authority audit for confirmed sale-completion evidence. That audit must locate the permanent sale-completion workflow, define completed-unit and completion-date authority, prove stable linkage to acquired inventory identity, and describe fail-closed behavior for incomplete or contradictory evidence before any Purchase Source Performance provider implementation is reconsidered.
