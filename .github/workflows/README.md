# GitHub Actions workflows

- `ci.yml` runs the required pull-request and main-branch validation gates.
- `windows-rc-package-gate.yml` is a manual package verification workflow for the portable Windows executable.
- `windows-rc-delivery.yml` is a manual, permission-scoped prerelease workflow. It builds and verifies the portable executable and installer, generates SHA-256 checksums, and publishes all three artifacts to a GitHub prerelease.
- Release publication is intentionally manual so a maintainer can choose the tag and release title after reviewing the exact main commit.
