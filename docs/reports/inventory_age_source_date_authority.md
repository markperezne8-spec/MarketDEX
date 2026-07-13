# Build 701G — Inventory Age Source-Date Authority Audit

**Status:** PREBUILD AUTHORITY AUDIT  
**Issue:** #254  
**Reports definition:** `inventory-age-patterns`

## Decision

The only currently approved candidate source date for Inventory Age is the Inventory-owned `purchase_date` exposed by `InventoryAppService.get_asset_detail()`.

This decision does not add runtime integration. It records the meaning and safety boundary that a later Inventory read contract must preserve.

## Repository evidence

- `InventoryAppService.get_asset_detail()` returns `purchase_date` from `inventory_business_details`.
- `InventoryAppService.update_business_details()` writes `purchase_date` through an audited Inventory command and preserves an Inventory business-details event.
- `assets.created_at` records application asset creation. It does not prove when Mark purchased or acquired the inventory.
- `inventory_history.recorded_at` records individual quantity/cost movements. It does not provide one stable acquisition date for the current position.
- `inventory_authority.verified_at` records authority verification timing. It is not an acquisition date.

Reports must not substitute application record creation, movement, or verification timestamps when `purchase_date` is missing.

## Business meaning

For the first Inventory Age report, age means:

> whole calendar days from the current Inventory-owned purchase date through an explicit report as-of date.

The report describes the current recorded purchase-date meaning. It does not reconstruct lot-layer age, weighted age, first-received age, time-since-listing, time-since-last-movement, or capital-cycle duration.

Those meanings require separate business questions and authority gates.

## Current data-quality limitation

`purchase_date` is optional and currently stored as trimmed text without an enforced date format.

A later read adapter must classify:

- blank value as **unavailable**;
- valid ISO `YYYY-MM-DD` value as **available**;
- nonblank value that is not a valid ISO calendar date as **invalid**;
- valid source date after the explicit as-of date as **invalid**.

Unavailable is not zero. Invalid text must not silently fall back to another timestamp.

Build 701G does not change existing Inventory write validation because doing so could affect current operator workflows and historical values.

## Read boundary

Future Reports integration must consume `purchase_date` through an approved Inventory query/read contract.

It must not:

- query `inventory_business_details` directly from Reports;
- open SQLite from Reports or presentation code;
- call Inventory mutation commands;
- change or normalize stored values;
- use `assets.created_at`, `inventory_history.recorded_at`, or `inventory_authority.verified_at` as fallback age dates;
- expand into Listing, Settlement, Pricing, Collection, or Market Intelligence authority.

## Next gate

After Build 701G merges, Build 701H may define a persistence-free Inventory Age source adapter contract that converts an approved Inventory detail mapping into explicit source-date evidence.

Build 701H may parse blank and ISO date strings into available, unavailable, or invalid evidence. It must not open a database, instantiate `InventoryAppService`, change Inventory writes, wire application composition, or execute a report query.

## Non-goals

Build 701G adds no runtime code, parser, query service, repository, schema, migration, calculation, threshold, chart, export, workspace, navigation, persistence, write, import, provider, network call, automation, or UI change.
