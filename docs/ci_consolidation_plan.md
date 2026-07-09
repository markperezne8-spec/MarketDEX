# MarketDEX CI Consolidation

## Problem

The repository accumulated many single-test GitHub Actions workflows. A pull request can therefore schedule dozens of independent runners even when the underlying verification is a pytest suite in one permanent codebase. This creates an operator-hostile Actions wall and delays exact-head verification.

## Target authority

`.github/workflows/marketdex-ci.yml` is the consolidated pull-request and main verification authority. It installs the project once and runs the complete pytest suite in one job.

The workflow uses concurrency cancellation so a newer commit on the same pull request cancels obsolete in-progress CI for the older head.

## Migration rule

Legacy gates are retired from automatic pull-request execution in controlled batches only after the consolidated workflow proves the same tests execute successfully. Tests remain in `tests/`; consolidation removes runner duplication, not verification coverage.

Manual Windows RC Delivery remains separate because packaging and release publication are operator-authorized release actions, not ordinary pull-request CI.

## Sequence

1. Establish consolidated full-suite CI.
2. Verify the full pytest suite through the consolidated job.
3. Inventory legacy automatic gate workflows by test coverage.
4. Retire duplicate automatic triggers in batches while preserving the tests.
5. Keep release delivery and genuinely distinct platform packaging workflows separate.
6. Require the consolidated MarketDEX CI result at the merge boundary.

## Guardrail

Do not delete business-authority tests to make CI faster. Consolidate execution authority; preserve test coverage and the permanent codebase.
