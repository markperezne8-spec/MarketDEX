# Release Candidate CI Note

Release-candidate checkpoint contract tests intentionally use the `release_candidate` test-name marker. Under the permanent five-gate CI surface, these contract tests are exercised by Core Tests through the shared `tests` collection when their names match the core service/schema selection boundary only if explicitly selected locally.

The authoritative permanent CI requirement remains the complete five-job result. The Windows operator checkpoint is a separate release verification action and is never represented as having passed solely because documentation contract tests pass.
