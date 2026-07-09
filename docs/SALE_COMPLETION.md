# Sale Completion

MarketDEX now separates listing execution from confirmed sale completion.

## Operator flow

Select an asset with an active recorded marketplace listing. Enter the marketplace order or sale reference, quantity sold, revenue, marketplace fees, shipping cost, and packaging cost. The operator explicitly confirms the sale as `SOLD`.

## Authority flow

The desktop orchestration reuses two permanent authorities in sequence:

`SalesService` records the completed sale, performs the single authoritative inventory decrement, and creates the single sales financial history event.

`MarketplaceLifecycleService` performs `SOLD_CONVERSION`, consuming the matching active listing allocation without creating a second inventory decrement or a second financial event.

The workflow fails closed when there is no active recorded listing, the sale quantity exceeds listing capacity, financial evidence is invalid, or explicit SOLD intent is absent.

## Offline boundary

MarketDEX does not infer sales, poll marketplaces, or modify remote marketplace state. The operator records confirmed marketplace evidence locally.
