# RC Delivery Decision Boundary

Decision: provide a repeatable operator-facing Windows RC package without committing generated binaries.

Build authority: `MarketDEX.spec` and `launcher.py`.

Delivery authority: manually dispatched `Windows RC Delivery` workflow.

Operator authority: download, extract outside the repository, and launch the verified package.

The delivery path does not install, update, publish marketplace listings, or alter cloud state.
