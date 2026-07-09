# Operator Sales Workspace Test Matrix

| Boundary | Verification |
| --- | --- |
| Listing preparation remains in Listings | Listing workflow widget tuple contains planning, readiness, preparation, review, and approved-package queue only. |
| Post-listing work moves to Sales | Sales workflow tuple owns listing execution history and sale completion. |
| No duplicated workflow widgets | Sales and Listings widget tuples are disjoint. |
| Operator navigation is explicit | Shell exposes dedicated `Listings` and `Sales` tabs. |
| Sales workspace remains scroll-safe | Shell retains the Sales scroll-area handle for viewport verification. |
| Authority semantics are preserved | Recomposition changes widget placement only; repositories and services are untouched. |
