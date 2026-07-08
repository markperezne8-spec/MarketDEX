# Inventory CSV Import Checkpoint

Accepted parent merge SHA: `a22eeec92310e20fd6b6efbe65eb96c899f66cf6`.

Visible workflow: Mission Control exposes Import CSV beside Export CSV. MarketDEX validates the complete LibreOffice-compatible export format before mutation, shows the validated asset count for confirmation, and imports each accepted row through the existing authoritative add-asset event path.

Validation rejects malformed headers, empty files, unsupported asset types, invalid quantity or cost values, duplicate CSV asset IDs, and asset IDs already present in MarketDEX before any import authority mutation begins.

Each imported row receives deterministic request identity beneath one import request prefix and produces verified inventory event, history, movement, and audit evidence. Protected M39-M165 authority remains append-only and unmodified.
