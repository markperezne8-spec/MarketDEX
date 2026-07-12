# MarketDEX Visual North Star and Mascot Standard

**Status:** 🔒 Design Locked · Permanent Product Requirement  
**Owner:** Product Owner  
**Applies to:** desktop UI, design system, charts, onboarding, gamification, packaging, installer, releases, future clients, and AI-generated interface work

## Authority

The Visual North Star and official mascot are central MarketDEX product authorities. They are not optional styling references, decorative extras, or temporary prototype material.

The detailed active implementation direction is defined in:

`docs/design/VISUAL_NORTH_STAR.md`

The reusable foundation is defined in:

- `docs/design/DESIGN_SYSTEM_FOUNDATION.md`
- `ui/design_system/tokens.py`
- `ui/design_system/component_contracts.py`

## Approved active visual asset

### Gamified Visual North Star v1

- Intended canonical path: `assets/brand/visual_north_star/marketdex_visual_north_star_v1.png`
- Dimensions: `1536 × 1024`
- Size: `2,863,520 bytes`
- SHA-256 identity: `1269e2af119c569cc5d4f76b82a6f92984a04f6f752119d8e1dcf417557909a5`
- Git blob identity when committed unchanged: `27d4b34b24984678225ae38c7e77240a02d521b4`
- Role: active quality benchmark for layout, hierarchy, polish, gamified engagement, personality, and desktop usability

The prior repository image `MarketDEX_Mission_Control_Visual_North_Star.png` remains historical design evidence. It may not be deleted by assumption, but it no longer supersedes the approved gamified v1 direction.

## Canonical mascot asset

- Current source path: `MarketDEX_Official_Mascot.png`
- Organized compatibility path: `assets/brand/mascot/marketdex_official_mascot.png`
- Dimensions: `1254 × 1254`
- SHA-256 identity: `32fad644bd5e8f6cfa4a3166913030fc4520ad0fef560943f4e432a5f39cebc4`
- Git blob identity: `5c192e8833896cf754f20fcb636d30098bc75ecf`
- Identity: Mark's original gray-and-white electric dog Pokémon character with yellow lightning accents and an energetic electric personality
- Role: permanent MarketDEX brand element

Replacing either approved asset requires explicit Product Owner approval, a documented reason, checkpoint update, identity-test update, and visual acceptance. Renaming, silently regenerating, recoloring, restyling, substituting, or deleting the mascot is prohibited.

## Product ambition

The finished MarketDEX desktop experience should meet or exceed the Visual North Star in:

- clarity
- usability
- polish
- cohesion
- personality
- engagement
- visual hierarchy
- information organization
- confidence and intelligence
- memorable product identity

The implementation does not need to copy the image literally. It may improve layouts and interactions while preserving the same ambition and recognizable MarketDEX character.

## Professional command center

MarketDEX should feel like a true collectibles business operating system rather than default forms or disconnected pages.

It should balance:

- professional business software
- collector enthusiasm
- Pokémon-inspired energy
- calm operational confidence
- meaningful gamification
- dense capability with understandable presentation

## Visual comprehension

Use the permanent flow:

> **Scan → Recognize → Understand → Investigate**

Primary decisions and attention appear first. Supporting visuals appear second. Evidence tables and raw history remain available through drill-down.

## Cohesion

Every workspace uses one shared design system for:

- typography
- spacing and density
- sizing
- semantic color roles
- iconography
- cards and panels
- tables
- buttons and controls
- forms and validation
- empty states
- status and confidence indicators
- charts and legends
- loading, success, warning, and error feedback
- navigation and workspace chrome
- optional progress and achievement surfaces

A feature may not invent an unrelated visual language or theme authority.

## Visual identity

The approved direction uses:

- deep navy structural surfaces
- bold blue, cyan, gold, red, green, and purple semantic accents
- readable high-contrast text
- crisp panel boundaries
- controlled glows and depth
- rounded but professional geometry
- strong numeric hierarchy
- meaningful icons and symbols
- balanced desktop density

Color must communicate meaning consistently and never carry essential meaning alone.

## Mascot integration

The mascot should be integrated intentionally, not pasted randomly onto screens.

### Recommended uses

- compact branding beside the MarketDEX wordmark
- assistant launcher
- welcome and first-run experience
- meaningful empty states
- loading and background-processing moments
- successful completion messages
- contextual guidance
- About MarketDEX
- installer and release artwork

### Usage limits

- Do not obstruct business information.
- Do not reduce table or chart readability.
- Do not repeat the mascot in routine panels.
- Do not use it for serious warnings where a neutral presentation is clearer.
- Do not animate it excessively.
- Do not stretch, destructively crop, recolor, or place it on backgrounds that destroy recognition.

The approved v1 direction intentionally keeps mascot presence compact and meaningful. The dashboard remains the focus.

## Gamification

Trainer levels, experience, badges, daily quests, achievements, milestones, and assistant encouragement are approved future capabilities and visual foundations.

They must:

- be optional
- reflect authoritative, useful activity
- never obscure financial or risk information
- never pressure unnecessary purchases, listings, or sales
- never reward incomplete or low-quality records
- remain visually subordinate to the operational workspace

## Workspace requirements

Every workspace defines:

1. primary user question
2. main action or decision
3. attention hierarchy
4. default summary information
5. progressive-disclosure path
6. empty state
7. loading state
8. error and recovery state
9. keyboard and accessibility behavior
10. design-system components used
11. mascot use or an explicit reason it is not appropriate
12. optional gamification impact or an explicit reason none is appropriate

## Data visualization requirements

Each chart requires:

- business question
- metric owner
- timeframe
- source coverage
- freshness
- confidence or evidence state
- accessible labels and supporting text
- drill-down path
- empty and insufficient-data state

Use line, bar, stacked-bar, pie/donut, heat-map, sparkline, and daily-volume visualizations only where their analytical purpose is clear.

## Design-system architecture

The desktop implementation establishes:

- versioned semantic design tokens
- typography and spacing scales
- density modes
- surface and border roles
- status and chart roles
- focus, hover, pressed, selected, disabled, loading, success, warning, and error states
- reusable component contracts and concrete widgets
- centralized asset resolution
- branded state patterns
- screenshot or visual-regression baselines

Widgets consume semantic tokens and reusable components rather than embedding unrelated colors, fonts, and spacing.

## Asset handling requirements

- Canonical source assets remain in the repository.
- Runtime code resolves assets through one brand manifest or asset service.
- Missing required assets produce a visible build, test, packaging, or startup failure.
- Silent fallback to a substitute mascot is prohibited.
- Development placeholders are clearly marked and cannot ship.
- Packaged executable and installer builds contain required assets.
- Asset paths work in source, packaged, installer, and installed-runtime contexts.

## Mandatory visual and brand gates

Before a visual feature or release is complete:

1. Visual North Star impact is documented.
2. The active v1 image is present at the canonical path and matches its approved identity.
3. The canonical mascot remains unchanged unless explicitly approved.
4. No substitute or temporary mascot is referenced.
5. New UI uses shared tokens and components.
6. Empty, loading, success, warning, and error states are reviewed.
7. Keyboard, focus, contrast, scaling, and non-color-only meaning are verified.
8. Common desktop resolutions and high-DPI behavior are verified.
9. Key workspace screenshots or visual baselines are reviewed.
10. Source runtime, packaged runtime, installer, and installed runtime include and resolve assets.
11. Gamification remains optional, meaningful, and non-disruptive.
12. Repository checkpoint history is updated.

## Fail-closed rules

- No release may silently omit the mascot or active Visual North Star asset.
- No missing mascot may be replaced by a generic icon.
- No redesign may remove the mascot from product identity.
- No major UI delivery may ignore `docs/design/VISUAL_NORTH_STAR.md` without an approved exception.
- No production build may contain an unapproved temporary mascot.
- No contributor may significantly alter the mascot's recognizable identity or electric personality without explicit Product Owner authorization.
- No visual transformation may claim completion when only a static mockup exists.
- No page-by-page visual rewrite may bypass the shared design system.

## Future platforms

Future iOS, Android, and web clients inherit the same brand authority, semantic design language, and canonical mascot. Platform-specific layouts may differ, but they may not create a replacement identity.

## Review rule

Every meaningful UI proposal should answer:

> **Does this move MarketDEX closer to the approved gamified Visual North Star while improving or preserving clarity, accessibility, performance, architecture, and operational trust?**

If not, the design requires refinement before production classification.