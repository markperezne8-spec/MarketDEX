# MarketDEX Architecture Gates

## Purpose

A gate is a mandatory pass/fail checkpoint that prevents work from advancing when the required evidence is missing. Gates protect architecture; they do not replace architecture.

## Gate hierarchy

1. **Authority gate** — confirms one canonical owner for data, schema, runtime, shell, and composition.
2. **Architecture gate** — confirms boundaries, dependencies, contracts, and no competing implementation path.
3. **Behavior gate** — proves business rules and user workflows with focused tests.
4. **Data gate** — proves persistence, migration, restart reconstruction, replay, audit, backup, and rollback safety.
5. **UX gate** — proves the interface is understandable, accessible, non-destructive, and decision-focused.
6. **Integration gate** — proves external data is normalized, attributable, fresh, confidence-scored, and isolated from business authority.
7. **Platform compatibility gate** — proves reusable domain and application logic remains independent from the current desktop UI and can support future clients without creating a second current application.
8. **AI safety gate** — proves AI-assisted actions use controlled commands, evidence, permissions, validation, and audit rather than direct database mutation.
9. **Packaging gate** — proves source runtime, packaged executable, installer, and installed runtime.
10. **Release gate** — requires all applicable gates, checkpoint updates, migration notes, and rollback evidence.

## Mandatory change checkpoint

Every material pull request must record:

- purpose and controlled scope
- canonical authority changed or preserved
- files and contracts added, changed, or retired
- schema and migration impact
- user-visible impact
- desktop impact and future-client compatibility impact
- AI-assisted workflow and audit impact when applicable
- tests and CI gates executed
- packaging or installer impact
- known limitations and deferred work
- exact next resume point
- PR number, head commit, and final CI result

A capability is not Complete merely because code exists. It is Complete only when its applicable permanent gate passes and repository-backed checkpoint history is updated.

## Fail-closed rules

- No second launcher, shell, database authority, schema owner, or feature registry.
- No active mobile or web application tree during the desktop-first phase.
- No reusable domain rule or calculation that requires a PySide6 widget.
- No direct external adapter writes to canonical business tables.
- No direct AI mutation of SQLite or authority tables.
- No migration without backup, transaction, validation, rollback planning, and historical fixture coverage.
- No recommendation without evidence, confidence, freshness, and explanation.
- No chart without a defined metric owner and decision purpose.
- No release with failing, skipped, or unrecorded required gates.

## Desktop-first platform rule

MarketDEX is currently a Windows desktop application. iOS, Android, and web browsers are future compatibility targets only. Current work must maximize desktop quality while keeping reusable domain, application, repository, provider, and data-transfer contracts presentation-independent.

## Collectibles extensibility rule

Pokémon TCG is the first optimized product experience. Shared architecture must use general collectible identities and contracts where appropriate so other TCGs, gaming products, graded items, Funko Pops, and related collectibles can be added through explicit category extensions rather than duplicate applications or hard-coded Pokémon-only business logic.

## Relative importance

Gates are the verification layer around the foundation. The strongest foundation order is:

1. product principles and authority model
2. domain and data model
3. architecture boundaries and composition
4. persistence and migration safety
5. feature and workspace contracts
6. platform-independent application contracts
7. observability, diagnostics, security, and AI safety
8. automated gates
9. UX refinement and feature expansion

A gate cannot rescue a poor architecture, but excellent architecture without gates will eventually regress.
