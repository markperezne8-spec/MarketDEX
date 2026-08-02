# CAP-012AM — Purchase Source Performance Provider Implementation Record

Issue #673 implements the narrow CAP-012AL provider slice. `PurchaseSourcePerformanceProvider` receives an Inventory acquisition reader and the existing `SaleCompletionQueryService` through its constructor, translates report dates to explicit UTC instants, joins only on canonical Inventory identity, and groups by exact trim-only purchase-source labels.

The provider returns immutable query evidence, preserves the incoming request, aggregates only authoritative acquired and completed-sale units, and fails closed for unavailable, conflicting, malformed, duplicate, out-of-period, or unrelated evidence. It performs no writes, persistence, registration, application composition, UI work, networking, retries, aliasing, or financial calculations. The existing calculator remains the formula authority.
