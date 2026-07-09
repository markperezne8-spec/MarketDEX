# Release Candidate Checkpoint PR

## Change summary

This change converts the next release boundary into an explicit release-candidate authority contract and Windows operator verification checkpoint.

## Why

MarketDEX already has the complete offline operator chain, runtime-data preservation coverage, a verified Windows executable path, and five permanent CI gates. The remaining release-hardening boundary needs one unambiguous definition of when a commit may be called a verified release candidate.

## Acceptance

- The five permanent CI jobs are named as mandatory release gates.
- Runtime operator data preservation is mandatory.
- The full Inventory → Pricing → Listing → Sale History operator chain remains in scope for desktop regression.
- Windows launch, relaunch, selection-aware handoff, and runtime preservation are covered by an operator checklist.
- Marketplace actions, LISTED outcomes, sale evidence, and SOLD conversion remain operator-authoritative.
- No marketplace polling, inferred sales, or remote mutation is introduced.
