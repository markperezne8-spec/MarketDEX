# MarketDEX Visual North Star and Mascot Standard

**Status:** 🔒 Design Locked · Permanent Product Requirement  
**Owner:** Product Owner  
**Applies to:** desktop UI, design system, charts, onboarding, packaging, installer, releases, future clients, and AI-generated interface work

## Authority

The Visual North Star and official mascot are central MarketDEX product authorities. They are not optional styling references, decorative extras, or temporary prototype material.

### Canonical visual asset

- Path: `MarketDEX_Mission_Control_Visual_North_Star.png`
- Git blob identity: `2ad414034ab1715c2f5019acc2ccff71f213706c`
- Role: primary inspiration and quality benchmark for MarketDEX layout, hierarchy, clarity, personality, polish, and visual ambition

### Canonical mascot asset

- Path: `MarketDEX_Official_Mascot.png`
- Git blob identity: `5c192e8833896cf754f20fcb636d30098bc75ecf`
- Identity: Mark's original gray-and-white electric dog Pokémon character with yellow lightning accents and energetic electric personality
- Role: permanent MarketDEX brand element

The recorded blob identities protect the exact approved source assets. Replacing either asset requires explicit Product Owner approval, a documented reason, checkpoint update, test update, and visual acceptance. Renaming, silently regenerating, recoloring, restyling, substituting, or deleting the mascot is prohibited.

## Product ambition

The finished MarketDEX desktop experience should meet or exceed the Visual North Star in:

- clarity
- usability
- polish
- cohesion
- personality
- visual hierarchy
- information organization
- confidence and intelligence
- memorable product identity

The implementation does not need to copy the image literally. It may improve layouts and interactions while preserving the same ambition and recognizable MarketDEX character.

## Visual design principles

### Professional command center

MarketDEX should feel like a true collectibles business operating system rather than a collection of default desktop forms.

The product should balance:

- professional business software
- collector enthusiasm
- Pokémon-inspired energy
- calm operational confidence
- dense capability with understandable presentation

### Visual comprehension

Use the established flow:

> **Scan → Recognize → Understand → Investigate**

Primary decisions and attention appear first. Supporting visuals appear second. Evidence tables and raw history remain available through drill-down.

### Cohesion

Every workspace should use one shared design system for:

- typography
- spacing
- sizing
- color roles
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

A new feature may not invent an unrelated visual language.

## Visual identity

The approved direction uses:

- bold red, blue, and yellow identity accents
- dark navy structural surfaces
- readable high-contrast content areas
- strong, organized panel boundaries
- color for meaning, hierarchy, and recognition rather than decoration
- icons and symbols where they improve comprehension
- balanced density suitable for a desktop productivity product

Exact tokens will be implemented through a versioned design-token system. Accessibility contrast and non-color-only meaning are mandatory.

## Mascot integration

The mascot should be integrated intentionally, not pasted randomly onto screens.

### Recommended uses

- welcome and first-run experience
- Mission Control identity area
- onboarding and contextual guidance
- meaningful empty states
- loading and background-processing moments
- successful completion messages
- About MarketDEX
- application branding
- installer and release artwork
- diagnostics or offline-status reassurance where appropriate

### Usage limits

- Do not obstruct business information.
- Do not reduce table or chart readability.
- Do not repeat the mascot in every panel.
- Do not use it for routine warnings where seriousness requires a neutral presentation.
- Do not animate it excessively.
- Do not stretch, crop destructively, recolor, or place it on backgrounds that destroy recognition.

The professional workflow remains primary. Mascot moments should add warmth, identity, guidance, or celebration.

## Workspace design requirements

Every workspace must define:

1. primary user question
2. main action or decision
3. attention hierarchy
4. default summary information
5. progressive disclosure path
6. empty state
7. loading state
8. error and recovery state
9. keyboard and accessibility behavior
10. mascot use or an explicit reason why mascot use is not appropriate

## Data visualization requirements

Charts must inherit the MarketDEX design system and Visual North Star ambition.

Each chart requires:

- a business question
- metric owner
- timeframe
- source coverage
- freshness
- confidence or evidence state
- accessible labels
- drill-down path
- empty and insufficient-data state

Use:

- line charts for change over time
- bars for comparison and ranking
- stacked bars for changing composition
- pie/donut charts only for understandable part-to-whole relationships
- heat maps for attention, concentration, and movement patterns
- sparklines for compact trends
- daily volume indicators for qualified observations

## Design-system architecture

The desktop implementation should establish:

- versioned semantic design tokens
- typography scale
- spacing scale
- surface and border roles
- status/severity roles
- chart roles
- focus, hover, pressed, selected, disabled, loading, success, warning, and error states
- reusable components
- asset-resolution service
- branded empty-state patterns
- screenshot or visual-regression baselines for key workspaces

Widgets should consume semantic tokens and reusable components rather than embedding unrelated colors, fonts, and spacing directly.

## Asset handling requirements

- The canonical source assets remain in the repository.
- Runtime code should resolve assets through one branded asset manifest or asset service.
- Missing required brand assets must produce a visible startup/build/test error.
- Silent fallback to a substitute mascot is prohibited.
- Development placeholders must be clearly marked and cannot ship.
- Packaged executable and installer builds must contain required assets.
- Asset paths must work in source, packaged executable, installer, and installed runtime contexts.

## Mandatory visual and brand gates

Before a visual feature or release is complete:

1. Visual North Star impact is documented.
2. Canonical mascot asset remains unchanged unless explicitly approved.
3. Required brand assets exist and have the expected identities.
4. No substitute or temporary mascot is referenced.
5. New UI uses shared design tokens and components.
6. Empty, loading, success, warning, and error states are reviewed.
7. Keyboard, focus, contrast, scaling, and non-color-only meaning are verified.
8. Key workspace screenshots or visual baselines are reviewed.
9. Source runtime, packaged runtime, installer, and installed runtime include and resolve assets.
10. Repository checkpoint history is updated.

## Fail-closed rules

- No release may silently omit the mascot.
- No missing mascot may be replaced at runtime by a generic icon.
- No redesign may remove the mascot from the product identity.
- No major UI delivery may ignore the Visual North Star without an approved documented exception.
- No production build may contain an unapproved temporary mascot.
- No contributor may significantly alter the mascot's recognizable identity or electric personality without explicit Product Owner authorization.

## Future platforms

Future iOS, Android, and web clients must inherit the same brand authority, semantic design language, and canonical mascot. Platform-specific layouts may differ, but they may not create a replacement identity.

## Review rule

The Visual North Star is a central quality benchmark. Every meaningful UI proposal should answer:

> **Does this make MarketDEX feel clearer, more intentional, more cohesive, more distinctive, and at least as ambitious as the approved Visual North Star?**

If not, the design requires refinement before production classification.