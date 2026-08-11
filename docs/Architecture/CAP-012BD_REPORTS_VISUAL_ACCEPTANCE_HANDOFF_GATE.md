# CAP-012BD — Reports Visual-Acceptance Handoff Gate

## Status

Documentation boundary for issue #711. This document records how Reports workspace UI preview PRs advance while a maximized Windows visual check is still pending.

## Purpose

Reports workspace UI previews can complete every non-visual gate before the user is at the PC. This keeps GitHub work moving without weakening the visual acceptance requirement for user-visible behavior.

## Pre-visual gates

A Reports UI preview PR may be prepared through these checks before a screenshot is available:

- the PR remains a draft while visual acceptance is pending;
- the exact PR head SHA is recorded;
- the changed-file list is inspected and kept within the approved issue boundary;
- the full PR patch is inspected for unauthorized runtime, persistence, provider, schema, automation, or mutation scope;
- review threads and submitted reviews are inspected;
- GitHub Actions CI is green for the exact PR head SHA;
- every workflow job in the CI run is completed successfully;
- the PR body states that a maximized Windows visual check is required before merge.

Passing these checks means the PR is non-visually ready. It does not authorize marking the PR ready for review or merging when the change affects visible UI.

## Visual handoff checklist

When the user returns to the PC, the handoff must tell the user exactly what to do:

1. Open GitHub Desktop.
2. Select the MarketDEX repository.
3. Switch to the active PR branch, not `main`.
4. Fetch origin and pull the PR branch.
5. Launch MarketDEX maximized.
6. Open the affected workspace.
7. Confirm the new surface is visible, readable, aligned with the North Star direction, and free of clipping or broken scroll behavior.
8. Send a screenshot for acceptance evidence.

The assistant must inspect the screenshot before marking the PR ready or merging.

## Merge constraints

For a user-visible Reports UI PR:

- do not merge while the visual check is missing;
- do not instruct the user to pull `main` before merge;
- do not mark ready until the visual check passes, CI is green, mergeability is confirmed, and the exact head SHA is unchanged;
- squash merge only with the expected head SHA;
- after merge, verify the PR and linked issue are closed, then tell the user to pull `main`.

## Away-from-PC handling

If the user is away from the PC, only non-visual work may continue. Acceptable work includes documentation, architecture classification, CI inspection, review-thread inspection, exact diff-scope review, and other clearly non-conflicting checks.

Away-from-PC work must not change the pending UI PR just to avoid visual acceptance. If the UI PR needs a visual repair, wait for screenshot evidence or create a clearly scoped follow-up once the issue is visible.

## Non-goals

This document authorizes no runtime behavior, UI styling, report execution, provider calls, schema changes, persistence, mutation authority, automation, merge bypass, or changes to PR #710.

## Verification

This boundary is documentation-only. CI must pass, but no visual check is required for this PR because it does not alter user-visible application behavior.
