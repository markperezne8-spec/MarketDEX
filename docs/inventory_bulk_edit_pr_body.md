## Inventory Bulk Edit

Adds visible multi-select bulk adjustment to MarketDEX Mission Control.

### Visible desktop workflow
Select two or more inventory rows, choose Bulk Adjust, enter one quantity delta and one cost delta per asset, review the selected count, confirm, and refresh Mission Control with authoritative inventory state.

### Authority safety
The complete selected set is validated before the first mutation. Missing assets and projected negative quantity or cost are blocked. Duplicate selected IDs are deduplicated. Accepted assets use the existing authoritative adjustment event path with exactly-once request identity, inventory history, movement, and verified audit evidence.

Protected M39-M165 authority remains append-only and unmodified.

Accepted parent: `4a04e33c2432e336ec0e6ab3b58cc8dfe8591b12`

DRAFT until the exact PR head integration and protected authority gates are GREEN.