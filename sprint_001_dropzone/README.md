# Sprint 001 Safe Code Drop Zone

This directory is a temporary staging area for Build Sprint 001 / RT-0.1.

Use the matching subfolder when adding code or evidence. Do not paste directly into production folders unless the target path has been reviewed.

## Folders

- `powershell/` — PowerShell scripts and local automation.
- `release_pipeline/` — Desktop CI, Listing CI, packaging, EXE, and installer changes.
- `mission_control/` — UI-only Mission Control and shell presentation work.
- `repository_stewardship/` — cleanup findings, naming audits, and technical-debt notes.
- `release_ops/` — release dashboard, checklist, diagnostics, and packaging verification.
- `engineering_receipts/` — work-package completion receipts.
- `screenshots/` — visual-review screenshots and notes.

## Safety rules

1. Keep one file name per responsibility.
2. Do not create `final`, `new`, `copy`, `latest`, or numbered duplicate filenames.
3. Do not include secrets, API keys, passwords, local databases, virtual environments, build outputs, or personal files.
4. Use descriptive names such as `start_sprint_001.ps1` or `desktop_ci_contract_fix.patch`.
5. Staged files are not production authority until reviewed and moved into their canonical repository locations.
