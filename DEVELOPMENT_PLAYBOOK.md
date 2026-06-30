# DEVELOPMENT_PLAYBOOK.md

# MarketDEX Development Playbook

## Purpose

This document defines how MarketDEX is planned, implemented, reviewed,
tested, documented, and released.

## Team Roles

### Product Owner

Defines vision, priorities, and acceptance.

### Jarvis (Chief Software Architect)

-   Owns architecture
-   Produces Build Packs
-   Reviews implementations
-   Maintains roadmap
-   Coordinates AI workflow

### Codex

Implements production-quality code from approved specifications.

### GitHub Copilot

Acts as pair programmer inside VS Code for explanations, refactoring,
and small improvements.

## Standard Build Workflow

Vision → Architecture → Specification → Build Pack → Codex → Copilot
Review → Windows Testing → Architecture Review → Git Commit →
Documentation → Release

## Every Build Pack Includes

1.  Architecture Brief
2.  Technical Specification
3.  Codex Prompt
4.  Copilot Prompt
5.  Test Plan
6.  Acceptance Checklist
7.  Git Commit Message
8.  Release Notes
9.  Documentation Updates
10. Next Milestone Preview

## Engineering Rules

-   Build reusable engines before features.
-   One responsibility per engine.
-   One responsibility per widget.
-   Dashboard-first design.
-   Visual-first presentation.
-   SQLite is the source of truth.
-   Offline-first.
-   Document major decisions.

## Definition of Done

A milestone is complete only when: - Code works - Architecture is
respected - Documentation updated - Windows tested - GitHub committed -
Ready for next milestone
