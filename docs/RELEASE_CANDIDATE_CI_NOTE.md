# Release Candidate CI Note

Release-candidate checkpoint contract tests intentionally use the `release_candidate` test-name marker. The permanent Core Tests job explicitly selects that marker so checkpoint contracts execute on pull requests and pushes to `main`.

The authoritative permanent CI requirement remains the complete five-job result. The Windows operator checkpoint is a separate release verification action and is never represented as having passed solely because documentation contract tests pass.
