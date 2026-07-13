# Market Intelligence SQLite Migration Plan

Build 700X documents the future SQLite migration boundary for the offline Market Intelligence warehouse. It is planning-only and does not create executable migrations, SQL files, adapters, repository implementations, seed data, or UI changes.

## Purpose

Market Intelligence will eventually need durable SQLite storage for approved offline evidence. Before any migration is implemented, the migration boundary must protect the existing offline-first architecture, Product Registry authority, provenance chain, and read-only Market Intelligence preview behavior.

## Ownership boundary

Future migration code will be owned by the Market Intelligence warehouse persistence layer. It must not be owned by UI pages, live-provider adapters, Product Registry services, pricing services, listing workflows, or inventory services.

Migration execution must be explicit and local. It must not contact networks, scrape marketplaces, fetch credentials, start schedulers, import live data, or mutate unrelated business-domain records.

## Schema-version boundary

Future migration execution must maintain a deterministic schema-version record before writing warehouse tables. Startup and repository construction should fail closed when the detected schema version is missing, newer than supported, partially applied, or inconsistent with expected table layout.

Schema-version checks must happen before repository writes. Repository interfaces should not silently create or upgrade tables as a side effect of normal reads.

## Future migration ordering

The first executable warehouse migration should create durable structures in dependency order:

1. sources, because provenance depends on source identity;
2. provenance, because observations depend on capture/source attribution;
3. observations, because snapshots and preview history depend on immutable evidence rows;
4. snapshots and snapshot-observation membership;
5. saved-query preview history, because it is a read-only history of derived preview output.

This ordering preserves append-only evidence semantics and makes failure recovery easier to reason about.

## Rollback and failure behavior

Future migrations must be atomic per migration step. A failed migration must leave the database at the previous known-good schema version or fail loudly with a recoverable error state. Partial table creation, partial data backfill, and mixed schema versions must not be treated as success.

Rollback behavior should be explicit. If automatic rollback is not safe, the migration layer should refuse to continue and report the exact migration/version that failed.

## Compatibility expectations

Future migrations must preserve existing Product Registry authority. Market Intelligence warehouse tables may reference product identifiers, but must not become the source of truth for product names, set metadata, inventory counts, listings, pricing records, or collection records.

Future migrations must preserve repository interface boundaries introduced before implementation. The migration layer prepares storage; repository adapters perform explicit read/write operations after schema compatibility is confirmed.

## Preview-history expectations

Saved-query preview history is future durable read-only history. A migration may create storage for preview history, but it must not introduce run, refresh, edit, import, delete, automation, or live-provider execution authority.

Preview history rows must be derived from approved offline evidence and tied to deterministic query identifiers, observation identifiers, and capture timestamps.

## Non-goals for Build 700X

- no SQL files;
- no SQLite connections;
- no executable migrations;
- no repository adapters;
- no repository implementations;
- no seed data;
- no imports or writes;
- no UI changes;
- no live providers, credentials, scraping, alerts, schedulers, or cloud sync;
- no mutation authority over Product Registry, inventory, pricing, listing workflow, collection, or other business-domain records.
