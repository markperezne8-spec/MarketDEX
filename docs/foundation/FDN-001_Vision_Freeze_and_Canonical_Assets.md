# FDN-001 — Vision Freeze and Canonical Asset Foundation

**Status:** Active first construction task  
**Authority:** Product Owner approval and EC-010  
**Branch:** `agent/market-intelligence-foundation`

## Objective

Establish a permanent, verifiable foundation baseline before production visual modernization begins.

## Deliverables

1. Preserve the Product Owner Vision Freeze decision.
2. Record repository, branch, stack, runtime, schema, packaging, asset, test, and known-defect baseline.
3. Synchronize the exact approved Visual North Star v1 PNG.
4. Promote v1 to required source and package authority.
5. Preserve the historical Visual North Star.
6. Preserve the exact permanent mascot.
7. Verify source, executable, installer, and installed-runtime resolution.
8. Fail visibly when a required brand asset is missing.
9. Update checkpoint, issue, and PR evidence.

## Required Visual North Star identity

Path:

`assets/brand/visual_north_star/marketdex_visual_north_star_v1.png`

Identity:

- `1536 × 1024`
- `2,863,520 bytes`
- SHA-256 `1269e2af119c569cc5d4f76b82a6f92984a04f6f752119d8e1dcf417557909a5`
- Git blob SHA `27d4b34b24984678225ae38c7e77240a02d521b4`

The file must not be regenerated, resized, compressed, converted, approximated, or substituted.

## Protected assets

- Active v1 target: `assets/brand/visual_north_star/marketdex_visual_north_star_v1.png`
- Historical evidence: `MarketDEX_Mission_Control_Visual_North_Star.png`
- Permanent mascot: `MarketDEX_Official_Mascot.png`

## Expected implementation surfaces

- `branding/asset_manifest.py`
- `MarketDEX.spec`
- `installer/MarketDEX.iss`
- brand-governance tests
- package and installer tests
- installed-runtime verification
- `FoundationCheckpoint.md`
- EC-010
- Issue #167
- PR #166 evidence

The actual changed-file set must remain evidence-driven and minimal.

## Exclusions

No Mission Control redesign, global theme rollout, new metrics, charts, gamification, schema changes, migrations, operator-data changes, workflow changes, workspace-ID changes, mascot changes, historical-asset removal, second shell, second launcher, second theme authority, merge, or release classification.

## Safety checks

- use isolated databases for automated runtime testing
- compare schema version before and after
- confirm runtime database path is unchanged
- confirm no seed/reset path is introduced
- confirm no operator records are mutated
- audit the changed-file list for unrelated scope
- stop if the image identity does not match exactly
- stop if the stack relationship changes

## Tests

Required focused evidence:

- exact active v1 identity
- exact mascot identity
- historical v0 preservation
- active/historical authority distinction
- missing-required-asset failure
- source asset resolution
- packaged executable inclusion and resolution
- installer inclusion
- installed-runtime resolution
- project-start authority
- architecture-governance authority
- no schema or migration change
- existing shell and runtime smoke checks

## Definition of done

FDN-001 is complete only after all required identities match, both required active assets resolve in every runtime form, historical evidence remains, missing assets fail visibly, no business/data behavior changes, applicable gates pass, and Product Owner review evidence is recorded.

## Next task

After Product Owner acceptance:

**FDN-002 — Controlled Root Theme Integration and Mission Control Header/KPI Reference Slice**

FDN-002 may migrate only the real Mission Control header and KPI presentation and must preserve every canonical snapshot key and refresh behavior.
