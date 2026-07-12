# CAP-006 Collection Read-only Implementation Slice

Status: provisional implementation boundary, hardened through CAP-006C

This slice adds a read-only Collection Overview projection over existing canonical
Product Registry, inventory, business-detail, and inventory-product-link authority.
It does not create a Collection write command, valuation model, grading workflow,
wishlist automation, portfolio/reporting logic, or market-data integration.

## Included

- linked Product Registry identity and canonical name;
- inventory quantity;
- storage location/custody evidence;
- acquisition date and source evidence;
- explicit empty and unmatched states;
- deterministic ordering and bounded search;
- visible `Not recorded` treatment for condition/grade and collector intent.

## Authority guardrail

Condition/grade and collector intent are not inferred from inventory fields. They
remain absent until a later authority decision defines their source, lifecycle,
and mutation contract. The workspace therefore remains safe to inspect without
creating false Collection facts.

The service remains a query-only projection. Product Registry, Inventory,
business-detail, and inventory-product-link tables remain the source authorities;
Collection reads must not insert, update, delete, or reinterpret their records.

## CAP-006C verification boundary

The focused read-model suite permanently verifies:

- deterministic ordering across repeated and restarted service instances;
- search by approved product name, product ID, asset ID, and storage location;
- bounded result limits and fail-closed invalid-limit handling;
- empty and unmatched behavior;
- unchanged row counts across all source-authority tables after reads;
- explicit absence of condition/grade and collector intent.

This verification strengthens the existing read model only. It does not satisfy
the CAP-006B gate for Collection-owned persistence or commands.

## Excluded

Valuation, profit, market intelligence, automated classification, grading
workflow, wishlist automation, Portfolio, Reports, and Collection mutations.
