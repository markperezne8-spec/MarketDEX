# MarketDEX Repository Hygiene Build R002

**Status:** DOCUMENTATION AUTHORITY RECONCILIATION COMPLETE
**Date:** 2026-07-05

## Authority Decision
`docs/standards/` is the single canonical standards tree.

The accidental nested path `docs/docs/standards/` was compared file-by-file against the canonical tree before removal.

## Proven Rule Merges
- `ENGINE_STANDARD.md`: preserved explicit responsibilities/non-responsibilities, public API, dependencies, error handling, strong typing, and docstring requirements.
- `MODULE_STANDARD.md`: preserved the rule that modules contain no business logic and do not access the database directly.
- `SPRINT_STANDARD.md`: preserved Testing and Retrospective as explicit sprint elements.
- `WIDGET_STANDARD.md`: preserved display-only/no-business-logic/no-database-access authority while explicitly preventing the old dashboard layout draft from becoming mandatory for every widget.

## Canonical Files Retained Without Rule Expansion
- `DECISION_STANDARD.md`
- `DOCUMENTATION_STANDARD.md`
- `GIT_STANDARD.md`
- `RELEASE_STANDARD.md`
- `TESTING_STANDARD.md`
- `UI_STANDARD.md`

## Verification
- All 10 canonical standards files remain under `docs/standards/`.
- `docs/docs/standards/` is removed.
- No Calc artifact was changed or deleted.
- No foundation document was changed.
- No checkpoint was changed.
- No Python source file was changed.
- No new business logic was invented.

## Next Recommended Movement
Repository Reconciliation should next repair repository entry-point and current-state authority documents before feature development resumes.
