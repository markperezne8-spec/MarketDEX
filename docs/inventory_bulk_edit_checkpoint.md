# Inventory Bulk Edit Checkpoint

Accepted parent merge SHA: `4a04e33c2432e336ec0e6ab3b58cc8dfe8591b12`.

Mission Control now supports extended row selection and exposes Bulk Adjust only when multiple inventory assets are selected. The operator enters one quantity delta and one cost delta per asset, reviews the selected asset count, and confirms the operation before mutation.

The complete selected set is validated before the first authoritative adjustment event. Any projected negative quantity or cost blocks the entire bulk request before mutation. Duplicate selected asset IDs are deduplicated.

Each accepted asset adjustment uses the existing authoritative inventory adjustment path with deterministic request identity beneath one bulk request prefix, inventory history, movement, verified audit evidence, and event verification. Protected M39-M165 authority remains append-only and unmodified.