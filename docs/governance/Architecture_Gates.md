# MarketDEX Architecture Gates

## Purpose

A gate is a mandatory pass/fail checkpoint that prevents work from advancing when required evidence is missing. Gates protect architecture; they do not replace architecture.

## Gate hierarchy

1. **Vision continuity gate** — confirms new ideas, approved recommendations, scope decisions, and superseded concepts are preserved in repository-backed product authority.
2. **Authority gate** — confirms one canonical owner for data, schema, runtime, shell, composition, and each business responsibility.
3. **Architecture gate** — confirms boundaries, dependencies, contracts, and no competing implementation path.
4. **Terminology compatibility gate** — confirms user-facing names are canonical, legacy aliases are mapped, and identifier changes have compatibility plans.
5. **Visual identity gate** — confirms the approved Visual North Star guides the interface, the exact official mascot remains canonical, and required brand assets survive source and packaged builds.
6. **Design-system gate** — confirms new UI uses semantic tokens, reusable components, defined states, and one shared interaction language rather than page-specific styling.
7. **Behavior gate** — proves business rules and user workflows with focused tests.
8. **Data gate** — proves persistence, migration, restart reconstruction, replay, audit, backup, and rollback safety.
9. **UX and accessibility gate** — proves the interface is understandable, keyboard-operable, scalable, non-destructive, progressively disclosed, and decision-focused.
10. **Integration gate** — proves external data is normalized, attributable, fresh, confidence-scored, and isolated from business authority.
11. **Platform compatibility gate** — proves reusable domain and application logic remains independent from the current desktop UI and can support future clients without creating a second current application.
12. **AI safety gate** — proves AI-assisted actions use controlled commands, evidence, permissions, validation, and audit rather than direct database mutation.
13. **Packaging gate** — proves source runtime, packaged executable, installer, installed runtime, and required brand assets.
14. **Release gate** — requires all applicable gates, checkpoint updates, migration notes, compatibility notes, visual acceptance, and rollback evidence.

## Mandatory change checkpoint

Every material pull request must record:

- purpose and controlled scope
- new, changed, rejected, or superseded product ideas
- `Product_Vision_Idea_Register.md` impact
- canonical terminology and legacy-name impact
- Visual North Star, mascot, gamification, and design-system impact
- canonical authority changed or preserved
- files and contracts added, changed, adapted, or retired
- schema and migration impact
- user-visible impact
- desktop impact and future-client compatibility impact
- AI-assisted workflow and audit impact when applicable
- tests and CI gates executed
- packaging, installer, high-DPI, and required-asset impact
- known limitations and deferred work
- exact next resume point
- PR number, head commit, and final CI result

A capability is not Complete merely because code exists. It is Complete only when its applicable permanent gates pass and repository-backed checkpoint history is updated.

## Fail-closed rules

- No material approved idea may exist only in chat memory.
- No new user-facing top-level name without a canonical terminology entry or an explicit statement that the existing term is reused.
- No rename of persisted IDs, import fields, API contracts, workspace IDs, or database values without compatibility mapping and regression evidence.
- No major UI delivery that ignores `docs/design/VISUAL_NORTH_STAR.md` without an approved documented exception.
- No replacement, deletion, redesign, recoloring, or silent substitution of the official MarketDEX mascot without explicit Product Owner approval.
- No release or installed build that omits required brand assets.
- No silent generic fallback when a required mascot or Visual North Star asset is missing.
- No new production page built primarily from one-off colors, spacing, states, or component styling when a shared design-system contract exists.
- No gamification that pressures unnecessary transactions, hides financial meaning, or rewards low-quality data.
- No second launcher, shell, database authority, schema owner, feature registry, or theme authority.
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

## Visual, mascot, and design-system authority

Primary active authority:

- `docs/design/VISUAL_NORTH_STAR.md`
- `docs/design/DESIGN_SYSTEM_FOUNDATION.md`
- `ui/design_system/tokens.py`
- `ui/design_system/component_contracts.py`

Approved active visual asset target:

- `assets/brand/visual_north_star/marketdex_visual_north_star_v1.png`
- SHA-256: `1269e2af119c569cc5d4f76b82a6f92984a04f6f752119d8e1dcf417557909a5`

Canonical mascot source:

- `MarketDEX_Official_Mascot.png`
- Git blob SHA: `5c192e8833896cf754f20fcb636d30098bc75ecf`

Historical visual evidence:

- `MarketDEX_Mission_Control_Visual_North_Star.png`

The historical image remains preserved, but the approved gamified v1 image is the active destination. Missing active or required assets must be visible in checkpoint, CI, packaging, or startup status; they may not be silently substituted.

## Desktop-first platform rule

MarketDEX is currently a Windows desktop application. iOS, Android, and web browsers are future compatibility targets only. Current work must maximize desktop quality while keeping reusable domain, application, repository, provider, and data-transfer contracts presentation-independent.

## Collectibles extensibility rule

Pokémon TCG is the first optimized product experience. Shared architecture must use general collectible identities and contracts where appropriate so other TCGs, gaming products, graded items, Funko Pops, and related collectibles can be added through explicit category extensions rather than duplicate applications or hard-coded Pokémon-only business logic.

## Relative importance

Gates are the verification layer around the foundation. The strongest foundation order is:

1. product vision, principles, and scope authority
2. canonical terminology and domain language
3. Visual North Star, mascot, design system, and accessibility
4. domain and data model
5. authority boundaries and application composition
6. persistence and migration safety
7. feature, module, command, query, event, and workspace contracts
8. platform-independent application contracts and read models
9. observability, diagnostics, security, and AI safety
10. automated gates and checkpoint history
11. incremental UX refinement and feature expansion

A gate cannot rescue poor architecture, but excellent architecture without gates will eventually regress.