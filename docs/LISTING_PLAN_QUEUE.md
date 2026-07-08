# Listing Plan Queue

The Listing Plan Queue turns persisted pricing decisions into an operator work queue.

## Operator flow

1. Select an active inventory asset.
2. Build and save its Listing Decision Workspace plan.
3. The saved plan appears in Listing Plan Queue.
4. Select the queued plan and choose Open Selected Plan.
5. MarketDEX returns to the authoritative inventory asset and restores the saved listing plan.

The queue is offline-first and derives from SQLite `listing_plans`; no marketplace publication occurs in this build.
