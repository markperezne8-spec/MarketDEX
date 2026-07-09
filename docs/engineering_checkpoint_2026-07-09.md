# MarketDEX Engineering Checkpoint — 2026-07-09

## Purpose

This checkpoint records the verified production boundary, active unmerged work, release evidence, current blocker, and exact restart control flow. Repository evidence is authoritative.

## Verified `main`

- Repository: `markperezne8-spec/MarketDEX`
- Verified `main` SHA at checkpoint creation: `11c9921271a4f0acb251ba362e6fcc0b3a19c42a`
- `main` includes PR #77: **Add operator-facing Windows RC delivery**.
- PR #76 repaired invalid Marketplace Listing Preparation GitHub Actions YAML workflows.
- Windows RC packaging uses `MarketDEX.spec`.
- `MarketDEX.exe` is generated release output and must not be committed to the permanent source repository.

## Verified Windows release boundary

The standalone Windows clean-launch boundary has been operator verified on a real Windows computer.

The manual **Windows RC Delivery** workflow was executed successfully. The resulting GitHub prerelease exposed `MarketDEX.exe` as a release asset. The operator downloaded the executable, passed the expected unsigned Windows SmartScreen boundary, and launched MarketDEX successfully.

This verifies operator-facing Windows RC delivery through GitHub Releases. It does not constitute code-signing verification.

## Verified business authority spine

The permanent codebase already carries the operational flow from inventory through pricing, listing preparation, listing execution history, and sale completion.

Authority remains in the existing services, repositories, SQLite persistence, pricing calculations, listing workflow, and SOLD conversion path. UI recomposition must preserve those boundaries rather than duplicate or replace them.

## Active unmerged work — PR #78

- PR: #78 — **Recompose MarketDEX into operator workspaces**
- Branch: `ui-operator-shell-recomposition`
- Base: `main`
- Exact head before this checkpoint commit: `0111dd2918e07d611e02f537d256e36d7a03a199`
- State at checkpoint creation: open, unmerged, mergeable

PR #78 responds to operator screenshots of the delivered Windows RC showing the legacy two-tab, vertically stacked experience.

The active shell target is:

`Mission Control → Inventory → Pricing → Listings → Sales`

The slice separates operator destinations while preserving existing business authority. Inventory hands off to Pricing; Pricing hands off to Listings; listing execution history and sale completion are separated into Sales.

## Verification state and blocker

The first PR #78 exact-head CI pass exposed stale two-tab contracts and documentation. Those contracts were repaired to describe the five-workspace shell.

After repair, GitHub Actions runs associated with exact head `0111dd2918e07d611e02f537d256e36d7a03a199` remained queued across repeated repository inspections. The observed state was `queued`, not `failure` and not `success`.

Therefore PR #78 is intentionally unmerged. The merge boundary is locked until exact-head verification executes and passes, or the Actions execution blockage is diagnosed and repaired.

## Restart control flow

On continuation:

1. Inspect live `main` SHA and PR #78 state. Do not trust this checkpoint over newer GitHub evidence.
2. Resolve the current PR #78 exact head, because this documentation commit advances the branch after `0111dd2918e07d611e02f537d256e36d7a03a199`.
3. Inspect exact-head GitHub Actions runs and runner execution state.
4. If Actions remain abnormally queued, investigate workflow/runner execution blockage instead of repeatedly waiting.
5. Repair defects first and keep changes on the existing production branch.
6. Verify the exact PR head with GitHub Actions.
7. Merge PR #78 only when the verification boundary is clean.
8. Only after `main` genuinely advances, instruct the operator to pull and provide the exact expected commit checkpoint.
9. Build and deliver the next Windows RC from merged `main` through the existing Windows RC Delivery authority.
10. Perform visual operator verification of the five-workspace shell on the real Windows executable.

## Operator state

At this checkpoint the operator has no required local action. No pull is required because PR #78 has not merged into `main`.

## Architectural guardrails

- Offline-first Windows desktop architecture.
- Permanent codebase; no prototype branches.
- Repair defects before adding scope.
- Preserve the existing authority spine.
- Smallest production-quality change that advances MarketDEX.
- Verify with tests and GitHub Actions before merge.
- Never commit `MarketDEX.exe` to source control.
- Repository evidence is the source of truth.
