# CAP-006 Collection Read-only Implementation Slice

Status: provisional implementation boundary

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

## Excluded

Valuation, profit, market intelligence, automated classification, grading
workflow, wishlist automation, Portfolio, Reports, and Collection mutations.
