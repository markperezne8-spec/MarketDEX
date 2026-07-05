# MarketDEX Development Playbook

**Version:** 2.0

**Status:** 📁 Repository Ready · 🔒 Design Locked

**Document Type:** Development Governance Living Document

**Permanent Filename:** `DEVELOPMENT_PLAYBOOK.md`

------------------------------------------------------------------------

## 🎯 Purpose

This document defines how approved MarketDEX knowledge moves into production implementation, focused debugging, verification, documentation, and release history.

Development is not the authority for inventing MarketDEX business logic.

The LibreOffice workbook remains the active proving ground and permanent business continuity system.

------------------------------------------------------------------------

## 🧭 Authority Chain

The normal implementation authority chain is:

💡 Idea

↓

📊 Spreadsheet Design

↓

💼 Real Business Use and Refinement

↓

🔒 Approved Business Responsibility

↓

🎨 Prototype Design when visual exploration adds value

↓

📦 Build Specification

↓

💻 Development

↓

🐞 Focused Debugging when required

↓

🧪 Verification

↓

📁 Git Commit and Documentation

↓

📦 Release History

Nothing gets coded until the relevant business responsibility has been discussed in Spreadsheet Design.

Prototype Design may define approved future presentation and interaction concepts.

Development implements proven ideas.

------------------------------------------------------------------------

## 🎯 Team Roles

### Mark — Product Owner

Mark defines vision, priorities, acceptance, and final project direction.

Mark is the final decision authority.

### Jarvis — Project Lead and Business Systems Architect

Jarvis:

- Protects approved MarketDEX architecture.
- Maintains planning and implementation boundaries.
- Converts approved responsibilities into implementation-ready specifications.
- Produces complete deliverables and Build Packs when practical.
- Reviews implementations against approved business logic.
- Coordinates specialist AI workflow.
- Protects repository continuity and checkpoint discipline.

### Codex — Implementation Specialist

Codex implements production-quality code from approved specifications.

Codex does not independently redesign MarketDEX business workflows or change locked business logic.

### GitHub Copilot — Pair Programming Support

GitHub Copilot may assist inside VS Code with explanations, local refactoring, and small implementation improvements.

Copilot suggestions do not override approved architecture or business logic.

------------------------------------------------------------------------

## 📊 Spreadsheet Design Authority

Spreadsheet Design is authoritative for current MarketDEX business workflows and business logic.

Approved responsibilities may include:

- Workbook workflows.
- Tables and historical records.
- Calculations and formulas.
- Controlled vocabularies.
- Validation rules.
- Derived statuses.
- Business event meaning.
- Decision-support logic.
- LibreOffice automation requirements.
- Authoritative and derived responsibility boundaries.

If Development discovers a contradiction, ambiguity, or potentially stronger business rule, implementation pauses on that issue and returns it to Spreadsheet Design.

Development must not resolve business-rule uncertainty by inventing production behavior.

------------------------------------------------------------------------

## 🎨 Prototype Design Authority

Prototype Design is authoritative for approved future application presentation concepts when those concepts have been reviewed and accepted.

Prototype work may define:

- Screen hierarchy.
- Navigation.
- Visual grouping.
- Interaction concepts.
- Read-oriented and action-oriented surfaces.
- MarketDEX visual-language application.
- Approved future desktop workflow presentation.

Prototypes do not create new business truth.

When a prototype requires a business-rule change, the issue returns to Spreadsheet Design.

------------------------------------------------------------------------

## 💻 Development Rules

Development exists only to implement proven ideas.

Engineering rules:

- Implement approved specifications.
- Preserve one permanent codebase.
- Prefer modular architecture.
- Keep one clear responsibility per engine or service when practical.
- Keep UI responsibilities understandable.
- Preserve stable identity and authoritative history.
- Preserve offline-first operation.
- Prefer free and subscription-resistant foundations when practical.
- Use SQLite as the desktop application's authoritative local data store unless a later approved architecture decision changes this.
- Document major engineering decisions.
- Do not redesign workflows during implementation.
- Do not change business logic during implementation.
- Do not invent unrelated features during implementation.

If implementation pressure suggests weakening an approved MarketDEX contract, return the issue to planning before changing direction.

------------------------------------------------------------------------

## 🐞 Debugging Rules

Debugging exists only for bugs.

For each bug:

1. Identify the root cause.
2. Recommend the smallest safe fix.
3. Explain why the issue occurred.
4. Apply or prepare the focused correction.
5. Verify the fix before moving on.

Do not redesign the application while fixing a bug.

Do not add roadmap work, architecture changes, or feature requests to a bug fix unless the root cause proves that an approved design contradiction exists.

A proven design contradiction returns to the appropriate planning responsibility.

------------------------------------------------------------------------

## 📦 Build Pack Standard

When a formal Build Pack is justified, it should include the implementation material necessary for the approved milestone.

The normal Build Pack may include:

1. Architecture Brief
2. Approved Responsibility Reference
3. Technical Specification
4. Codex Prompt
5. Copilot Review Prompt when useful
6. Test Plan
7. Acceptance Checklist
8. Git Commit Message
9. Release Notes
10. Documentation Updates
11. Next Milestone Preview

Build Packs should not recreate unresolved planning inside Development.

------------------------------------------------------------------------

## 🧪 Verification Standard

Implementation should be verified against the approved responsibility before release.

Verification should confirm:

- The intended workflow works.
- Approved business logic is preserved.
- Authoritative and derived responsibilities remain correctly separated.
- Historical evidence is not silently overwritten.
- UI behavior matches approved prototype direction when applicable.
- Offline-first expectations remain intact.
- The implementation does not introduce unrelated features.
- Relevant Windows behavior is tested.
- Documentation is synchronized when the milestone changes permanent project knowledge.

------------------------------------------------------------------------

## 📦 Release Discipline

Releases preserve the historical record of MarketDEX evolution.

A milestone is complete only when the applicable work is:

- Implemented.
- Verified.
- Consistent with approved architecture.
- Documented.
- Windows tested when applicable.
- Committed to GitHub.
- Ready for the next approved milestone.

Release history records completed work.

Nothing is developed or debugged in the Releases responsibility.

------------------------------------------------------------------------

## 🚀 Current Phase

The active proving ground is LibreOffice Calc Version 0.

Broad pre-build business architecture is frozen enough for workbook execution.

Future desktop application development may begin gradually only from proven and approved Spreadsheet Design or Prototype Design responsibilities and only when Mark authorizes that movement.

The workbook remains permanent and must not be treated as disposable because software implementation begins.

------------------------------------------------------------------------

## 📁 Document Governance

**Permanent Filename:** `DEVELOPMENT_PLAYBOOK.md`

**Current Version:** 2.0

**Status:** 📁 Repository Ready · 🔒 Design Locked · 🏁 Checkpoint Complete · 👍 Approved

**Purpose:** Define the permanent governance boundary between approved MarketDEX planning, production implementation, focused debugging, verification, and release history.

**Safe to Replace Repository Copy**
