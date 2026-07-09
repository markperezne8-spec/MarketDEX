# Windows RC Operator Delivery

## Purpose

Provide a deliberate operator-facing Windows Release Candidate package without committing generated executables to the permanent source repository.

## Authority boundary

- The Git repository remains source authority.
- `MarketDEX.exe` remains a generated build product.
- The Windows RC Delivery workflow is manually dispatched when an operator package is required.
- The package contains `MarketDEX.exe` and a short `README.txt` with launch and repository-separation guidance.
- The operator extracts and runs the package outside the source repository.

## Delivery sequence

`source authority -> Windows build -> executable verification -> operator package staging -> artifact publication -> operator retrieval -> clean launch`

## Non-goals

This boundary does not add marketplace connectivity, cloud persistence, automatic updating, installer registration, or source-controlled binaries.
