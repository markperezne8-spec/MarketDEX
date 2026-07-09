# PR — Restore direct Pricing and Listing Workflow access

## Problem
The Pricing and Listing Workflow tabs were disabled until an inventory row was selected. In live operator use this made both primary workspaces appear broken and impossible to open.

## Change
- Keep Pricing and Listing Workflow tabs enabled at all times.
- Keep asset selection as the authority for guided Continue buttons.
- Do not force the operator back to Inventory when selection clears.
- Update viewport tests to enforce direct workspace access.

## Acceptance
An operator can click Pricing or Listing Workflow immediately. Selecting an asset enables the guided handoff buttons and preserves the intended Inventory → Pricing → Listing Workflow flow.
