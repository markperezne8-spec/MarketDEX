# Release Candidate Checkpoint Change Summary

This milestone does not add a new business feature. It turns the existing 99% release-hardening boundary into an enforceable final checkpoint.

MarketDEX now has one explicit definition of release-candidate authority: all five permanent CI jobs must pass, existing operator runtime data must be preserved, the packaged Windows app must launch and relaunch against that data, Inventory → Pricing → Listing selection context must survive the operator handoff, and marketplace/sale outcomes remain operator-controlled.

The `release_candidate` contract suite is wired into Core Tests. Windows execution is still pending and cannot be inferred from green documentation contracts.
