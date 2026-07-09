# MarketDEX CI Consolidation

## Problem

The repository accumulated many single-test GitHub Actions workflows. A pull request can therefore schedule dozens of independent runners even when the underlying verification is a pytest suite in one permanent codebase. This creates an operator-hostile Actions wall and delays exact-head verification.

## Target authority

`.github/workflows/marketdex-ci.yml` is the consolidated pull-request and main verification authority. It installs the project once and runs the complete pytest suite in one job.

The workflow uses concurrency cancellation so a newer commit on the same pull request cancels obsolete in-progress CI for the older head.

## Migration rule

Legacy gates are retired from automatic pull-request execution in controlled batches only when their commands are strict subsets of the consolidated `python -m pytest -q` suite. Tests remain in `tests/`; consolidation removes runner duplication, not verification coverage.

Manual Windows RC Delivery remains separate because packaging and release publication are operator-authorized release actions, not ordinary pull-request CI.

## Retirement batches

The first controlled batch retires five milestone authority workflow files: M51-M55, M71-M75, M101-M105, M126-M130, and M136-M140.

The second controlled batch retires five duplicate feature gates: Viewport Fit, Listing Plan Queue, Listing Plan Queue Contract, Listing Plan Persistence, and Operator Sale Completion. Their pytest targets remain in `tests/` and are discovered by the consolidated full-suite command.

The third controlled batch retires five cumulative milestone gates: M66-M70, M81-M85, M106-M110, M116-M120, and M151-M155. Each gate only installed the same runtime and executed an explicit subset of tests already discovered by the consolidated full-suite command.

No test file is deleted. No service, repository, SQLite, UI, pricing, listing, or sale authority is changed.

## Sequence

1. Establish consolidated full-suite CI.
2. Confirm duplicate legacy gate commands are subsets of full-suite pytest discovery.
3. Retire duplicate automatic gates in controlled batches while preserving the tests.
4. Verify the consolidated full pytest suite through the exact-head job.
5. Keep release delivery and genuinely distinct platform packaging workflows separate.
6. Require the consolidated MarketDEX CI result at the merge boundary.

## Guardrail

Do not delete business-authority tests to make CI faster. Consolidate execution authority; preserve test coverage and the permanent codebase.
