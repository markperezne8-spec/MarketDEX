# MarketDEX Development Playbook

**Version:** 2.1
**Status:** 📁 Repository Ready · 🔒 Design Locked
**Document Type:** Development Governance Living Document
**Permanent Filename:** `DEVELOPMENT_PLAYBOOK.md`

---

## 🎯 Purpose
This document defines how proven MarketDEX knowledge moves into implementation, focused debugging, verification, repository preservation, and release history.

Development is not the authority for inventing MarketDEX business logic.

The LibreOffice workbook remains the active proving ground and permanent business continuity system.

## 🧭 Authority Chain
`💡 Idea → 📊 Spreadsheet Design → 💼 Real Business Use and Refinement → 🔒 Approved Business Responsibility → 🎨 Prototype Design when visual exploration adds value → 📦 Build Specification when needed → 💻 Implementation → 🐞 Focused Debugging when required → 🧪 Verification → 📁 Repository Preservation → 📦 Release History`

Nothing gets coded until the relevant business responsibility has been discussed and approved in Spreadsheet Design.

Prototype Design may define approved future presentation and interaction concepts.

Implementation implements proven ideas. It does not redesign them silently.

## 🎯 Team Roles
### Mark — Product Owner
Mark defines vision, priorities, acceptance, and final project direction.

Mark is the final decision authority and performs business or visual acceptance when appropriate.

Mark is not expected to manually perform implementation work Jarvis can reasonably complete.

### Jarvis — Project Lead and Business Systems Architect
Jarvis protects approved MarketDEX architecture; maintains planning and implementation boundaries; converts approved responsibilities into implementation-ready work; produces complete deliverables; directly maintains repository text authority when safe tools are available; reviews implementation against approved business logic; coordinates specialist AI workflow; and protects repository continuity and checkpoint discipline.

For routine design-locked LibreOffice Calc work, Jarvis may implement and package the build directly when the approved baseline ODS is available and a safe package-inspection path exists.

### Codex — Selective Implementation Specialist
Codex is reserved for production-quality code, high-risk native ODS work, difficult debugging, or milestone verification when specialist value materially improves safety or quality.

Codex does not independently redesign MarketDEX business workflows or change locked business logic.

Codex is not required for every routine Calc build.

### GitHub Copilot — Pair Programming Support
GitHub Copilot may assist inside VS Code with explanations, local refactoring, and small implementation improvements.

Copilot suggestions do not override approved architecture or business logic.

## 📊 Spreadsheet Design Authority
Spreadsheet Design is authoritative for current workbook workflows and business logic.

Implementation contradictions return to Spreadsheet Design before locked business logic changes.

The workbook proves the business system. Later technology may reduce friction around proven knowledge.

## 🏗️ Routine Workbook Build Flow
`Mark approves → Jarvis builds → Jarvis verifies → Jarvis provides finished downloadable ODS → Mark visually checks → approved build is repository-preserved`

Jarvis should use the smallest sufficient verification path.

Mark should not be asked to edit XML, rebuild ODS packages, recreate design-locked workbook sections, or perform repetitive implementation steps Jarvis can safely complete.

## 🔗 Repository Preservation Flow
When Jarvis can safely perform repository text maintenance directly:
`Inspect authority → make the smallest approved change → verify → commit directly to GitHub → tell Mark to Pull origin`

When a binary workbook artifact cannot be safely written directly through the available repository path:
`Jarvis creates verified download → Mark visually accepts → Mark places finished artifact in approved repository path → commit/push only when Jarvis cannot safely perform that preservation step directly`

Do not ask Mark to push or replace files merely from habit. First determine whether Jarvis can safely perform the operation.

## 🐞 Debugging Boundary
Debugging exists only for focused defect repair.

Use:
`Root cause → smallest safe fix → explanation → verification`

Do not redesign architecture, change business logic, or add unrelated features while fixing a bug.

If a defect reveals a better workflow idea, return that idea to the correct planning responsibility before changing direction.

## 🧪 Verification Discipline
Verification should be proportional to risk.

Routine design-locked workbook builds may use package integrity, native mimetype structure, XML parseability, design-lock evidence checks, and Mark's visual acceptance when appropriate.

High-risk native ODS changes, difficult package defects, or milestone verification may justify Codex or additional specialist review.

Repeated verification that adds no meaningful confidence should be avoided.

## 📦 Release and Checkpoint Discipline
Releases preserve meaningful milestones, packages, and engineering decisions. Nothing is developed or debugged in the Releases responsibility lane.

Checkpoints preserve current continuity and approved knowledge when enough meaningful progress has accumulated or context risk is increasing.

Design-locked and repository-preserved work must not be rediscovered unless new evidence, a defect, or Mark explicitly reopens the decision.

## 🏗️ 📐 🛑 Recommendation Standard
- 🏗️ **BUILD** — implementation, creation, packaging, or preservation.
- 📐 **PLAN** — discovery, blueprint, business logic, architecture, or next movement.
- 🛑 **STOP** — intentional hold, blocker, checkpoint, or do-not-proceed boundary.

## 📁 Document Governance
**Permanent Filename:** `DEVELOPMENT_PLAYBOOK.md`

**Current Version:** 2.1

**Status:** 📁 Repository Ready · 🔒 Design Locked · 🏁 Checkpoint Complete · 👍 Approved

**Purpose:** Define the implementation, debugging, verification, repository-preservation, and release workflow for proven MarketDEX knowledge.

**Safe to Replace Repository Copy**