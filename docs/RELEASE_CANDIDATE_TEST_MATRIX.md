# Release Candidate Test Matrix

| Boundary | Automated contract | Windows operator checkpoint |
| --- | --- | --- |
| Permanent CI surface | Exactly five named jobs | Confirm candidate commit is green |
| Startup | Runtime preservation contract | Launch packaged executable |
| Runtime data | Non-empty operator DB preservation | Confirm inventory survives launch and relaunch |
| Inventory handoff | Existing feature regression suite | Select inventory item |
| Pricing handoff | Existing feature regression suite | Confirm selected item context |
| Listing handoff | Existing feature regression suite | Continue into Listing with same context |
| Listing planning | Planning/sale separation contract | Confirm saved plans remain planning records |
| Marketplace authority | No remote side-effect contract | Confirm no remote marketplace action |
| Sale authority | Explicit evidence and SOLD conversion contracts | Confirm no inferred sale completion |

A Windows checkpoint failure blocks release-candidate verification and becomes a focused release-hardening defect. No unrelated feature expansion is allowed inside that repair boundary.
