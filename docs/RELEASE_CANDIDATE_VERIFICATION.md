# Release Candidate Verification

Before calling a MarketDEX commit a verified release candidate, the operator performs this local Windows checkpoint:

- Pull the exact candidate commit from `main`.
- Confirm the existing runtime database is present before launch when testing preservation.
- Launch the packaged `MarketDEX.exe`.
- Confirm Mission Control opens without a startup error.
- Open Inventory and confirm existing operator inventory remains present.
- Select an inventory item and verify the Pricing handoff is selection-aware.
- Continue from Pricing into Listing and verify the selected item remains the active operator context.
- Confirm saved listing plans remain separate from sale completion.
- Confirm no marketplace action is performed remotely by MarketDEX.
- Close and relaunch the application, then confirm runtime inventory is still preserved.

The release candidate is verified only after the five permanent CI gates are green and this Windows checkpoint passes against the candidate build.
