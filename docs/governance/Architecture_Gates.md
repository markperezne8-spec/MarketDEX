# MarketDEX Architecture Gates

## Purpose

A gate is a mandatory pass/fail checkpoint that prevents work from advancing when the required evidence is missing. Gates protect architecture; they do not replace architecture.

## Gate hierarchy

1. **Vision continuity gate** — confirms new ideas, approved recommendations, scope decisions, and superseded concepts are preserved in repository-backed product authority.
2. **Authority gate** — confirms one canonical owner for data, schema, runtime, shell, composition, and each business responsibility.
3. **Architecture gate** — confirms boundaries, dependencies, contracts, and no competing implementation path.
4. **Terminology compatibility gate** — confirms user-facing names are canonical, legacy aliases are mapped, and identifier changes have compatibility plans.
5. **Behavior gate** — proves business rules and user workflows with focused tests.
6. **Data gate** — proves persistence, migration, restart reconstruction, replay, audit, backup, and rollback safety.
7. **UX gate** — proves the interface is understandable, accessible, non-destructive, progressively disclosed, and decision-focused.
8. **Integration gate** — proves external data is normalized, attributable, fresh, confidence-scored, and isolated from business authority.
9. **Platform compatibility gate** — proves reusable domain and application logic remains independent from the current desktop UI and can support future clients without creating a second current application.
10. **AI safety gate** — proves AI-assisted actions use controlled commands, evidence, permissions, validation, and audit rather than direct database mutation.
11. **Packaging gate** — proves source runtime, packaged executable, installer, and installed runtime.
12. **Release gate** — requires all applicable gates, checkpoint updates, migration notes, compatibility notes, and rollback evidence.

## Mandatory change checkpoint

Every material pull request must record:

- purpose and controlled scope
- new, changed, rejected, or superseded product ideas
- `Product_Vision_Idea_Register.md` impact
- canonical terminology and legacy-name impact
- canonical authority changed or preserved
- files and contracts added, changed, adapted, or retired
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

- No material approved idea may exist only in chat memory.
- No new user-facing top-level name without a canonical terminology entry or an explicit statement that the existing term is reused.
- No rename of persisted IDs, import fields, API contracts, workspace IDs, or database values without compatibility mapping and regression evidence.
- No second launcher, shell, database authority, schema owner, or feature registry.
- No active mobile or web application tree during the desktop-first phase.
- No reusable domain rule or calculation that requires a PySide6 widget.
- No direct external adapter writes to canonical business tables.
- No direct AI mutation of SQLite or authority tables.
- No migration without backup, transaction, validation, rollback planning, and historical fixture coverage.
- No recommendation without evidence, confidence, freshness, and explanation.
- No chart without a defined metric owner and decision purpose.
- No release with failing, skipped, or unrecorded required gates.

## Vision and idea authority

`docs/governance/Product_Vision_Idea_Register.md` is the living approved product-direction register.

Every material idea is classified as:

- APPROVED — CURRENT
- APPROVED — FOUNDATION
- APPROVED — FUTURE
- RESEARCH
- REJECTED/SUPERSEDED

A newer explicit Product Owner decision may supersede an older idea, but the reason and replacement must remain discoverable.

## Naming authority

`docs/governance/Canonical_Product_Terminology.md` controls new user-facing terminology.

The terminology gate distinguishes:

- user-facing labels
- stable internal IDs
- persisted identifiers
- legacy aliases
- compatibility migrations

A UI text clarification may happen before an internal identifier migration. Internal and persisted renames require a controlled compatibility change.

## Desktop-first platform rule

MarketDEX is currently a Windows desktop application. iOS, Android, and web browsers are future compatibility targets only. Current work must maximize desktop quality while keeping reusable domain, application, repository, provider, and data-transfer contracts presentation-independent.

## Collectibles extensibility rule

Pokémon TCG is the first optimized product experience. Shared architecture must use general collectible identities and contracts where appropriate so other TCGs, gaming products, graded items, Funko Pops, and related collectibles can be added through explicit category extensions rather than duplicate applications or hard-coded Pokémon-only business logic.

## Relative importance

Gates are the verification layer around the foundation. The strongest foundation order is:

1. product vision, principles, and scope authority
2. canonical terminology and domain language
3. domain and data model
4. authority boundaries and application composition
5. persistence and migration safety
6. feature, module, command, query, event, and workspace contracts
7. platform-independent application contracts and read models
8. observability, diagnostics, security, and AI safety
9. automated gates and checkpoint history
10. UX refinement and feature expansion

A gate cannot rescue poor architecture, but excellent architecture without gates will eventually regress.