# Inventory Sorting Checkpoint

MarketDEX Mission Control now exposes read-only inventory sorting.

## Visible workflow

The inventory panel provides Sort by and direction controls. Operators can sort the current inventory projection by NAME, TYPE, QUANTITY, or TOTAL COST in ASC or DESC order. Search and asset-type filters compose with sorting and the visible result label reports the active sort.

## Authority boundary

Sorting is a projection-only operation. It does not append event identity, inventory history, inventory movement, or audit authority records. Unsupported sort keys and directions are rejected explicitly.

## Accepted parent

`80f63688b118c2ab82c3865f2bb554b0db055fba`

This checkpoint remains draft until the exact PR head integration gate and protected M39-M165 authority spine are GREEN.