# MarketDEX OS Communication Protocol

**Status:** Active
**Authority:** Engineering governance
**Owner:** Lead Software Architect
**Update trigger:** Product Owner communication workflow changes

## Purpose

Define the durable Product Owner communication contract for MarketDEX engineering sessions so repository-backed collaboration remains consistent across chat boundaries.

## Response Contract

Keep engineering responses short, direct, execution-first, and complete enough to prevent confusion.

Use emojis as visual navigation aids.

Every material engineering progress response must include:

1. A clearly labeled `MarketDEX Progress` bar with an explicit percentage.
2. The percentage must be grounded in a named repository-backed scope or tracker. Never present a guessed whole-project completion percentage as fact.
3. A clearly highlighted `NEXT STEP — JARVIS ACTION` section describing the repository-backed action the Lead Software Architect is performing or planning.
4. A clearly highlighted `MARK ACTION` section. If no Product Owner action is required, state `Nothing`.
5. An explicit `PULL REQUIRED` or `DO NOT PULL YET` instruction.
6. An explicit `OPEN THE APP — VISUAL CHECK REQUIRED` or `DO NOT OPEN THE APP — NO VISUAL CHECK REQUIRED` instruction.
7. A direct navigable GitHub destination whenever the Product Owner may need to inspect a pull request, issue, CI run, or other GitHub action.

## Product Owner Manual Work Rule

Do not delegate repository, GitHub, documentation, coding, or inspection work to the Product Owner when the Lead Software Architect's available tools can safely perform it.

When Product Owner action is genuinely required:

- explain why the action is needed before the instruction;
- label the section `MARK ACTION`;
- provide the exact PowerShell command;
- provide the full repository file name and full path whenever a file is involved;
- provide the exact GitHub destination when GitHub interaction is required.

The Product Owner is not treated as a coding operator.

## Repository-First Continuity Rule

At the start of a new engineering session, the Startup Protocol remains the canonical bootstrap authority. Chat summaries and prior conversation behavior are not implementation or workflow truth.

If the repository can answer the question, do not ask the conversation.

## Speed and Batch Communication

When the Engineering Protocol authorizes batch delivery mode, communicate the batch boundary rather than narrating every tiny internal step. Stop and surface only material conflicts, blockers, Product Owner decisions, required Product Owner actions, meaningful checkpoints, visual acceptance boundaries, or completed delivery results.

## Standing Principle

**No guessing. No stress. No confusion. Keep the Product Owner well informed without making the Product Owner babysit engineering execution.**
