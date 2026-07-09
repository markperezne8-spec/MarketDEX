# MarketDEX OS Desktop Architecture

## Status
Foundation baseline for desktop application version `0.1.0-foundation`.

## Authority
The LibreOffice ODS business specification in `artifacts/calc/` is the authoritative source of business behavior. Desktop code implements the specification and does not independently redefine business rules.

## Architecture

UI Layer
↓
Application Service Layer
↓
Domain Layer
↓
Repository Ports
↓
SQLite Adapters / Import-Export Adapters

## Layer Responsibilities

### UI
PySide6 windows, pages, dialogs, widgets, navigation, and user interaction. No SQL and no authoritative business rules.

### Application Services
Orchestrate use cases and workflows. Coordinate domain rules, repositories, and audit behavior.

### Domain
Business entities, value concepts, invariants, and workbook-defined business rules. Independent of PySide6 and SQLite.

### Repository Ports
Define persistence interfaces required by the domain and application services.

### Adapters
Implement repository ports and external boundaries. SQLite is the primary offline persistence adapter. Import and export adapters remain replaceable.

## Engineering Rules

1. Offline-first; no subscription dependency.
2. Business rules do not live in UI code.
3. SQL does not live in UI code.
4. Persistence is accessed through repository boundaries.
5. Type hints are required for production Python code.
6. Application behavior must trace to the business specification.
7. Verification must trace to requirements where applicable.
8. `main` must remain releasable.
9. Audit events are append-oriented and immutable where the specification requires preservation.
10. No prototype branches or parallel permanent codebases.

## First Vertical Slice
Inventory is the first end-to-end domain after the application foundation is operational.
