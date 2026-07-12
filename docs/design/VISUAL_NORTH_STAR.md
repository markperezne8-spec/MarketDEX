# MarketDEX Visual North Star

**Status:** 🔒 Design Locked · Permanent Product Direction  
**Approved:** 2026-07-11  
**Owner:** Product Owner  
**Current delivery target:** Windows desktop  
**Future compatibility:** iOS, Android, and browser clients may inherit the design language later; they are not current implementation targets

## Purpose

This document establishes the approved gamified MarketDEX dashboard concept as the official long-term Visual North Star for the application shell, navigation, dashboards, workspaces, components, information hierarchy, branding, interaction language, and overall user experience.

The Visual North Star is a destination and quality standard. It is not permission for a single uncontrolled rewrite, a disconnected prototype, invented production data, or replacement of proven business logic.

MarketDEX should evolve toward this direction through reusable, modular, accessible, testable foundations while preserving existing functionality, data, workflows, packaging, and repository authority.

## Canonical approved visual identity

### Approved Visual North Star v1

- Intended canonical path: `assets/brand/visual_north_star/marketdex_visual_north_star_v1.png`
- Approved source dimensions: `1536 × 1024`
- Approved source size: `2,863,520 bytes`
- SHA-256 identity: `1269e2af119c569cc5d4f76b82a6f92984a04f6f752119d8e1dcf417557909a5`
- Git blob identity when committed unchanged: `27d4b34b24984678225ae38c7e77240a02d521b4`
- Role: official future UI quality benchmark and product-direction reference

The earlier repository visual at `MarketDEX_Mission_Control_Visual_North_Star.png` remains preserved as historical design evidence. It must not be deleted merely because this v1 direction supersedes it as the active visual destination.

### Canonical mascot

- Current canonical source path: `MarketDEX_Official_Mascot.png`
- Future organized path: `assets/brand/mascot/marketdex_official_mascot.png`
- Source dimensions: `1254 × 1254`
- SHA-256 identity: `32fad644bd5e8f6cfa4a3166913030fc4520ad0fef560943f4e432a5f39cebc4`
- Git blob identity: `5c192e8833896cf754f20fcb636d30098bc75ecf`

The gray-and-white electric dog Pokémon with yellow lightning accents is the permanent MarketDEX mascot. It may not be replaced, removed, significantly redesigned, recolored, restyled, or silently substituted without explicit Product Owner approval.

## Product experience goal

MarketDEX should feel like one cohesive Pokémon TCG business and collecting operating system designed for collectors, sellers, investors, graders, and business operators.

It should communicate:

- intelligence
- confidence
- organization
- speed
- professionalism
- collector personality
- business readiness
- clear decision support
- premium desktop quality
- recognizable MarketDEX identity

It must not feel like a generic database, a spreadsheet replacement, or unrelated desktop forms placed beside each other.

The interface should be visually exciting without becoming confusing, Pokémon-inspired without becoming childish, and professionally useful without becoming cold or generic.

## Permanent experience principles

> **Enter once. Understand everywhere.**

> **Decisions first. Evidence second. Raw metrics on demand.**

> **Scan → Recognize → Understand → Investigate.**

Every major screen should help the user answer:

1. What is happening?
2. Why does it matter?
3. What requires attention?
4. What can I do next?
5. How fresh, reliable, and explainable is the information?

Decoration must improve recognition, hierarchy, confidence, or engagement. It must never hide financial meaning, evidence quality, operational risk, or primary actions.

## Overall visual language

The approved direction is a dark, polished, energetic command-center interface using:

- deep navy and dark-blue backgrounds
- layered surfaces with clear visual depth
- bright blue, cyan, gold, red, green, and purple accents
- high-contrast information presentation
- controlled glow and highlight effects
- crisp panel borders
- rounded but professional geometry
- strong headings and readable numeric displays
- clear separation among navigation, status, metrics, analysis, and actions
- dense information arranged through understandable hierarchy

### Semantic color roles

- **Green:** positive performance, completion, healthy status, verified success
- **Red:** risk, urgent attention, loss, failure, or destructive action
- **Gold / Yellow:** opportunity, recommendation, achievement, important attention
- **Blue / Cyan:** navigation, information, standard actions, data exploration
- **Purple:** collection, research, secondary intelligence, collector-oriented areas
- **Neutral navy / gray:** structure, support, inactive states, secondary evidence

Meaning must not depend on color alone. Text, icon, shape, position, or pattern must reinforce important status.

### Effects

Gradients, glows, shadows, borders, and motion should support hierarchy and delight while remaining controlled. Effects may not create noise, reduce contrast, impair performance, or make the app look like a game menu instead of a serious operating system.

## Application shell

The application shell is the stable visual and behavioral frame around all MarketDEX modules.

It should eventually contain:

- branded top header
- persistent left navigation
- global status and reporting controls
- central workspace host
- contextual alerts and actions
- global search or command access
- current operating mode
- data freshness and application health
- notification count
- assistant access
- appropriate progress and engagement surfaces

Individual modules may contribute workspaces and context, but may not replace or redesign the shell independently.

## Left navigation

The left navigation should provide:

- clear active-workspace state
- consistent icons
- readable labels
- logical grouping
- strong spacing and alignment
- keyboard accessibility
- collapsed and expanded behavior where justified
- tooltips when labels are hidden
- persistent access to essential workspaces

Potential groups include:

- Operations
- Collection
- Market Intelligence
- Business Management
- Reports and Analysis
- Utilities
- System

Exact group order must be validated against real workflows and canonical product terminology.

## Global status area

The top status area should use real application data for:

- active reporting period
- current business date
- last market-data refresh
- database status
- backup status
- import status
- offline / connected state
- application health
- active profile or mode
- notification count

A decorative status label may not imply a capability or connection that does not exist.

## Mission Control

Mission Control is the flagship implementation of the Visual North Star and the first complete production-quality reference workspace.

It should summarize the operation without forcing the user to inspect every module.

### Primary KPI candidates

- total portfolio value
- total inventory value
- total collection value
- net profit
- units sold
- cash available
- active listings
- inventory ROI
- average cost per unit
- potential value
- sales performance
- collection completion

Each KPI card requires:

- clear label
- prominent value
- relevant comparison period
- direction and magnitude of change
- evidence or authority state
- drill-down destination
- calculation explanation

The UI must distinguish confirmed, imported, manually entered, estimated, market-derived, and recommended values.

## Dashboard panel architecture

Dashboard pages should compose reusable panels rather than one-off layouts.

Approved panel families include:

- portfolio value trend
- inventory composition
- collection composition
- market sentiment
- daily sales volume
- Needs Attention / alerts
- opportunities
- risk warnings
- sealed-product decisions
- price-per-pack calculations
- marketplace performance
- collection overview
- market comparisons
- listing performance
- Collector Pulse trends
- research insights
- progress and achievements

Every panel must define:

- purpose and business question
- authoritative owner
- data source
- refresh behavior
- loading state
- empty state
- insufficient-data state
- error and recovery state
- drill-down destination
- accessibility behavior
- calculation explanation
- fact / estimate / recommendation classification

Production panels may not display invented data as real information.

## Charts and data visualization

Charts exist to answer business questions, not merely to decorate the dashboard.

The reusable chart foundation should support:

- line charts for value, price, profit, supply, and performance over time
- bar charts for marketplace, category, product, and ranking comparisons
- stacked bars for composition over time
- pie / donut charts for understandable part-to-whole relationships only
- sparklines for compact movement
- heat maps for attention, opportunity, concentration, and movement patterns
- daily sold-volume indicators
- supply and listing-count movement
- market-sentiment composites
- 7-day, 30-day, 90-day, 1-year, and all-history ranges

Every chart requires:

- clear labels and units
- readable axes where applicable
- useful tooltips
- controlled time range
- source coverage
- freshness
- confidence or evidence state
- accessible supporting text
- consistent numeric formatting
- drill-down path
- empty, unavailable, and insufficient-data states

## Opportunities, risks, and recommendations

The interface must visually distinguish:

- opportunities
- risks
- informational insights
- confirmed events
- recommended actions

Every recommendation must answer:

- What is recommended?
- Why?
- What evidence supports it?
- How fresh is the evidence?
- What assumptions were used?
- What risks or alternatives exist?
- What action can the user take?
- How confident is MarketDEX?

Guidance such as KEEP, WATCH, CONSIDER SELLING, GRADE, OPEN, BREAK, KEEP SEALED, REPRICE, LIST, WAIT, or REDEPLOY CAPITAL must remain explainable and user-controlled.

## Marketplace and listing experience

Marketplace panels may eventually display:

- active listings
- sold items
- sales value
- conversion rate
- time to sale
- marketplace fees
- estimated and actual net proceeds
- listing health
- inventory aging
- price competitiveness
- stock readiness
- suggested actions

The interface must preserve clear boundaries among:

- user-recorded marketplace information
- imported observations
- prepared listing packages
- operator-confirmed actions
- remote marketplace actions
- recommendations

Visual modernization does not authorize marketplace polling, automated publication, inferred sales, or remote mutation without separately approved capabilities and gates.

## Business Mode and Collector Mode

Business Mode and Collector Mode are permanent presentation lenses over shared authoritative data. They are not separate applications or databases.

### Business Mode prioritizes

- profit and ROI
- inventory turnover and aging
- listing readiness
- sales and expenses
- marketplace fees
- cash deployment
- orders, fulfillment, and settlement
- operational alerts

### Collector Mode prioritizes

- collection completion
- set progress
- personal value
- grading goals
- card and product discovery
- trade planning
- wishlist progress
- collector insights
- keep, watch, trade, sell, open, or keep-sealed analysis

The app should remember the last-used mode and provide an obvious, accessible mode switch.

## Mascot integration

The mascot is central to MarketDEX identity but must not dominate business workflows.

### Appropriate uses

- compact product branding in the header
- Mission Control identity area
- assistant launcher
- welcome and onboarding
- meaningful empty states
- contextual tips
- loading or processing states
- success moments
- About MarketDEX
- installer and packaging artwork

### Usage limits

- do not obstruct metrics, charts, tables, or actions
- do not repeat the mascot in every panel
- do not use it for serious warnings where neutral presentation is clearer
- do not animate excessively
- do not distort, destructively crop, recolor, or restyle it
- do not use temporary or substitute mascots in production

The approved dashboard direction intentionally reduces mascot dominance: one small, recognizable mascot near the MarketDEX brand and carefully selected contextual moments are preferred over repeated mascot images.

## Gamification and engagement

Gamification is an approved future capability and visual foundation requirement. It should make accurate, useful work feel rewarding without pressuring users or trivializing business decisions.

Approved concepts include:

- trainer level
- experience progress
- badges
- daily quests or objectives
- achievements
- collection milestones
- business milestones
- optional assistant encouragement

Meaningful activities may include:

- completing accurate inventory records
- recording purchase costs
- resolving data-quality issues
- preparing eligible inventory for listing
- completing confirmed sales workflows
- maintaining backups
- reviewing important alerts
- completing a set
- reaching collection goals
- improving fulfillment quality

Gamification must be optional, respectful, non-disruptive, and based on authoritative activity. It may never hide important financial information, encourage unnecessary transactions, or reward low-quality data entry.

## Design-system foundation

Before broad page redesign, MarketDEX must establish one canonical design system covering:

- semantic colors
- typography
- spacing
- component sizes
- corners and radii
- borders
- shadows and elevation
- icon sizes
- motion
- focus states
- hover, pressed, selected, disabled, loading, success, warning, and error states
- chart roles
- status roles
- density levels
- high-DPI scaling

The system should support:

- standard desktop density
- compact data-heavy density
- large-text accessibility
- high-DPI monitors
- practical window sizes
- future theme evolution

Individual widgets may not embed unrelated visual values when a semantic token exists.

## Reusable component foundation

Initial shared components should include:

- application shell
- navigation item
- workspace header
- KPI card
- dashboard panel
- status badge
- alert row
- opportunity card
- recommendation card
- chart container
- data table
- filter bar
- search control
- segmented control
- primary and secondary buttons
- mode selector
- empty state
- loading state
- error state
- confirmation dialog
- detail drawer
- mascot guidance panel
- assistant launcher
- progress / achievement card

Every component requires defined states, spacing, keyboard behavior, accessibility requirements, tests, example usage, and clear code ownership.

## Information hierarchy

The normal visual priority is:

1. global status
2. primary KPIs
3. important trends
4. Needs Attention, opportunities, and risks
5. current workflows
6. supporting details and evidence
7. optional progress and engagement

Not every panel must appear simultaneously. Layouts should respond to real data, screen size, user priorities, mode, and density.

## Accessibility and usability

The visual system must support:

- sufficient text contrast
- keyboard navigation
- visible focus states
- screen-reader labels where supported
- scalable text
- high-DPI rendering
- color-vision accessibility
- reduced-motion preferences
- clear hover, selected, and pressed states
- readable tables
- deliberate text truncation
- minimum control sizes
- window resizing
- common desktop resolutions

Visual similarity never overrides usability.

## Performance and offline-first requirements

The Visual North Star must be implemented without abandoning MarketDEX principles.

The application should remain:

- fast to start
- responsive during navigation
- reliable offline
- safe with existing user data
- modular and testable
- packagable as a Windows desktop application
- free from unnecessary subscriptions and cloud requirements

Images, icons, themes, and components should be packaged locally. Missing required assets must fail visibly in development, testing, packaging, or startup rather than silently disappearing.

Heavy dashboards should load incrementally. A slow or unavailable data source must not freeze the entire application.

## Phased implementation

### Phase 0 — Preserve and checkpoint

- preserve the approved image identity and canonical target path
- confirm and protect the mascot
- establish this design authority
- establish a formal checkpoint
- record current branch, release, tests, and limitations
- avoid broad UI rewriting

### Phase 1 — Audit the current application

- map shell, pages, components, styles, and assets
- identify duplicated styling
- identify reusable widgets
- document inconsistencies
- identify UI/business coupling
- classify what can be upgraded safely

### Phase 2 — Establish design tokens

- semantic color roles
- typography
- spacing and density
- borders, corners, depth, and states
- chart and status colors
- accessibility rules
- central theme access

### Phase 3 — Build reusable components

- shell primitives
- navigation
- KPI cards and dashboard panels
- buttons, inputs, badges, tables, and states
- component tests and examples

### Phase 4 — Upgrade the shell

- branded header
- improved left navigation
- global status area
- compact mascot integration
- preserved routes and workflows

### Phase 5 — Build Mission Control reference workspace

Mission Control must prove:

- real data supports the design
- shared components are reusable
- performance remains acceptable
- practical resolutions work
- recommendations remain explainable
- navigation and drill-down work
- mascot integration remains professional

### Phase 6 — Migrate workspaces incrementally

Each migration must preserve:

- existing data
- service boundaries
- business logic
- user workflows
- tests
- import/export behavior
- packaging reliability

### Phase 7 — Add advanced visual features

After the foundation is stable, consider:

- refined animation
- richer assistant experiences
- gamification
- achievements and daily objectives
- advanced charts
- personalized dashboards
- workspace customization
- additional mascot moments

## Prohibited approaches

Do not:

- attempt one massive UI rewrite
- replace stable business logic to change appearance
- build every page with one-off styling
- introduce competing theme systems
- use mock data as production data
- sacrifice readability for effects
- remove or replace the mascot
- lose or ignore the Visual North Star
- introduce unnecessary online dependencies
- break inventory, listing, sale, or settlement workflows
- overwrite or reseed user data
- build a beautiful shell disconnected from real services
- treat this direction as a disposable prototype
- claim completion when only a static mockup exists

## Initial acceptance criteria

The first Visual North Star foundation milestone is complete only when:

- the approved image is stored at its canonical repository path
- its identity and approval are documented
- a formal checkpoint exists
- the mascot is identified and protected
- the current UI is audited
- central semantic design tokens exist
- foundational reusable components are defined
- at least one real workspace uses them
- existing data remains intact
- existing workflows continue to function
- packaging includes required assets
- high-DPI and common-window behavior are tested
- missing brand assets are detected visibly
- the result moves toward the approved image without creating an isolated prototype

## Evaluation rule

Every meaningful UI proposal, PR, and release must answer:

> **Does this move MarketDEX measurably closer to the approved Visual North Star while preserving comprehension, accessibility, performance, data authority, and existing workflows?**

A proposal that looks polished but weakens clarity, evidence, accessibility, architecture, or operational safety does not pass.