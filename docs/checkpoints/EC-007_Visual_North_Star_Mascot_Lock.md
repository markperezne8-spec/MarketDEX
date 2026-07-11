# EC-007 — Visual North Star and Mascot Lock

**Checkpoint date:** 2026-07-11  
**Status:** Visual identity governance complete; full UI implementation remains future work  
**Authority:** Product Owner approval, canonical repository assets, Visual North Star standard, brand manifest, and permanent tests

## Product Owner decision

The Product Owner approved all current recommendations that remain consistent with MarketDEX architecture, product principles, and release requirements.

The Product Owner also established the Visual North Star and official electric dog Pokémon mascot as permanent, non-optional product requirements.

## Canonical assets verified

### Visual North Star

- Path: `MarketDEX_Mission_Control_Visual_North_Star.png`
- Git blob identity: `2ad414034ab1715c2f5019acc2ccff71f213706c`
- Result: PRESENT and protected

### Official mascot

- Path: `MarketDEX_Official_Mascot.png`
- Git blob identity: `5c192e8833896cf754f20fcb636d30098bc75ecf`
- Result: PRESENT and protected

The official mascot remains Mark's original gray-and-white electric dog Pokémon with yellow lightning accents and an energetic electric identity.

## Permanent requirements established

- The Visual North Star is a central quality benchmark, not a minor style reference.
- MarketDEX should meet or exceed its clarity, ambition, polish, personality, and usability.
- The mascot may not be replaced, removed, significantly redesigned, recolored, or silently substituted.
- The canonical source assets remain repository authority.
- Mascot use should be intentional and integrated, not distracting.
- Appropriate uses include Mission Control, welcome/onboarding, empty states, processing, success moments, About, application identity, installer, and release artwork.
- UI redesign, packaging, and release work must preserve both assets.
- Missing assets must fail visibly rather than degrade silently.

## New architecture and governance

### Visual standard

Added:

`docs/governance/Visual_North_Star_and_Mascot_Standard.md`

This standard controls:

- visual ambition and product quality
- layout and hierarchy
- design-system cohesion
- typography, spacing, color, components, tables, forms, and charts
- empty/loading/success/warning/error states
- accessibility and progressive disclosure
- mascot placement and usage limits
- source, package, installer, and installed-runtime asset requirements

### Brand asset manifest

Added:

`branding/asset_manifest.py`

This provides one application-facing source for required brand assets and deliberately raises an error when a canonical asset is missing. It provides no substitute mascot fallback.

### Permanent tests

Added:

`tests/test_brand_asset_governance.py`

The test verifies:

- both files exist
- both are non-empty PNG assets
- both match the exact approved asset identities
- both are documented as permanent requirements
- changes require explicit approval and checkpoint updates

Architecture governance tests now protect the Visual identity gate and this checkpoint.

## Expanded mandatory gate stack

1. Vision Continuity
2. Authority
3. Architecture
4. Terminology Compatibility
5. **Visual Identity and Brand Assets**
6. Behavior
7. Data and Migration
8. UX and Accessibility
9. Integration and Provenance
10. Platform Compatibility
11. AI Safety
12. Packaging and Installed Runtime
13. Release and Checkpoint

## Gate status

| Gate | Result | Evidence |
|---|---|---|
| Vision Continuity | PASS | Product Owner direction preserved in repository checkpoint |
| Visual identity | PASS FOR FOUNDATION | Standard, exact assets, manifest, and identity tests established |
| Mascot protection | PASS FOR FOUNDATION | Canonical mascot path and blob identity protected |
| Architecture | PASS FOR FOUNDATION | Brand assets isolated behind one manifest and shared design-system direction |
| UX | DESIGN PASS | Visual quality, consistency, accessibility, states, and usage rules documented |
| Packaging | REQUIREMENT RECORDED | Full packaged and installed asset inclusion must be verified when UI packaging integration is implemented |
| Behavior | NOT CHANGED | No existing workflow behavior changed |
| Release | BLOCKED | Existing stacked PR and Listing-gate conditions remain unresolved |

## Known limitations

- The current desktop UI has not yet been redesigned to fully implement the Visual North Star.
- The mascot has not yet been placed throughout the production desktop interface.
- The current packaging definition has not yet been changed to consume the brand manifest.
- Screenshot/visual regression baselines have not yet been created.
- The existing Listing CI issue remains intentionally deferred under current Product Owner direction.

## Required implementation sequence

1. Establish semantic design tokens and reusable desktop components.
2. Create a centralized packaged asset resolver using the brand manifest.
3. Include canonical assets in source, executable, installer, and installed runtime.
4. Add visible missing-asset startup/build failures.
5. Apply the Visual North Star to Mission Control and the application shell first.
6. Add intentional mascot integration to welcome, Mission Control, empty/loading/success, About, and packaging surfaces.
7. Add visual regression or screenshot review for major workspaces.
8. Verify keyboard, focus, scaling, contrast, non-color-only status, and layout resilience.

## Exact resume point

1. Continue canonical domain and persistence architecture planning.
2. Keep visual identity and mascot requirements attached to every future UI, packaging, and release specification.
3. Before the first major desktop redesign, define the MarketDEX design-token and component-system specification.
4. Before the first branded production package, connect `branding/asset_manifest.py` to packaging and installed-runtime tests.
5. Return to the Listing CI failure before any stacked PR is marked ready or merged.

## Non-negotiable continuity rule

Future contributors and AI assistants must read this checkpoint and `Visual_North_Star_and_Mascot_Standard.md` before changing MarketDEX UI, branding, packaging, installer assets, or product identity.

The exact approved asset identities remain protected until the Product Owner explicitly unlocks them.