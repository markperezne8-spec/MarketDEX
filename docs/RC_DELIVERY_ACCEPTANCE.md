# RC Delivery Acceptance

The operator-facing Windows RC delivery boundary is accepted only when:

1. The manual Windows RC Delivery workflow is recognized by GitHub Actions.
2. The Windows build produces a non-empty `MarketDEX.exe`.
3. The executable is staged with `README.txt` guidance.
4. The operator package is published as `MarketDEX-Windows-RC-Operator-Package`.
5. The operator can download, extract outside the repository, and clean-launch MarketDEX.

Until all five conditions are verified, the delivery boundary remains active.
