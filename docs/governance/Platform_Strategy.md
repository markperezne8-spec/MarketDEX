# MarketDEX Platform Strategy

## Current delivery target

MarketDEX is a Windows desktop application first. Current implementation, optimization, packaging, testing, and UX decisions must prioritize making the desktop product excellent for people and AI-assisted workflows.

No iOS, Android, or browser application is currently in scope.

## Future compatibility direction

Future clients may include:

- iOS
- Android
- web browsers

These are compatibility constraints, not current delivery commitments. Desktop development must not be slowed by premature mobile or web UI work.

## Permanent architecture rule

Reusable business capabilities must remain independent from PySide6 and Windows-specific presentation wherever practical.

The intended long-term separation is:

```text
Domain rules and calculations
        ↓
Application commands, queries, and services
        ↓
Repository and provider interfaces
        ↓
Desktop UI today / future mobile or web clients later
```

PySide6 widgets may depend on application contracts. Domain rules, pricing logic, marketplace normalization, recommendations, and persistence contracts must not depend on PySide6 widgets.

## Desktop-first boundaries

- One Windows desktop launcher and one application shell remain authoritative.
- SQLite remains the current offline-first local persistence engine.
- Windows executable and installer verification remain mandatory release gates.
- Desktop keyboard, mouse, large-screen, accessibility, and productivity workflows receive current UX priority.
- No responsive mobile layout, mobile packaging, browser deployment, cloud synchronization, or multi-device account system is required now.

## Future-compatible requirements

New reusable capabilities should use:

- stable string identities rather than tab indexes or widget references
- typed commands, queries, events, and data-transfer contracts
- repository and provider protocols
- deterministic calculations without UI dependencies
- serializable values and timestamps
- explicit schema and API versioning
- source, freshness, confidence, and audit metadata
- replaceable marketplace and trend adapters

## Collectibles scope

Pokémon TCG selling is the first optimized workflow. The permanent domain model must avoid hard-coding Pokémon-only assumptions where a general collectible concept is appropriate.

Future supported categories may include:

- other trading card games
- sealed gaming products
- graded cards
- Funko Pops
- gaming collectibles
- related collectible products

Shared concepts should include Product, Variant, Edition, Condition, Grading, Inventory Asset, Marketplace Listing, Sale, Market Observation, Collection Position, and Attention Signal. Category-specific fields belong in explicit extensions rather than duplicate application trees.

## AI usability direction

MarketDEX should be easy for both people and authorized AI assistants to operate safely through the same application rules.

Future AI assistance must use controlled commands and read models rather than direct database mutation. Recommendations must remain explainable, evidence-linked, confidence-scored, freshness-aware, and subject to the same authority and audit gates as human actions.
