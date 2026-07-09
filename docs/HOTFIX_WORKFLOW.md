# MarketDEX Surgical Hotfix Workflow

## Permanent lesson from the workspace-tab regression

Small regressions must remain small.

1. Reproduce the exact operator-visible failure.
2. Identify the smallest runtime cause.
3. Create one clean branch from current `main`.
4. Change the minimum implementation files required.
5. Update the existing authoritative regression test when old tests encode broken behavior.
6. Audit CI dependencies and the complete runtime → tests → CI path before opening the PR.
7. Keep the PR surgical. If branch history or changed-file scope becomes unexpectedly large, stop and rebuild cleanly from `main`.
8. Use the permanent five-gate MarketDEX CI. Do not create workflow floods or temporary permanent gates.
9. Do not merge until required CI is green.
10. Do not tell Mark to pull until the merged commit is on `main`.
11. Give Mark one exact operator acceptance test after pull.
12. Report status directly: ZERO ACTION FOR MARK when no action is required; PULL NOW only when pull authority is real.

## Anti-patterns

- Documentation floods during a surgical fix.
- Dozens of repository writes for one regression.
- Reacting to CI failures one layer at a time without auditing the whole validation chain.
- Carrying a contaminated branch forward.
- Declaring a repair nearly done before tests and CI dependencies are aligned.

## Default hotfix sequence

REPRODUCE → ROOT CAUSE → CLEAN BRANCH → MINIMUM FIX → AUTHORITATIVE TEST → CI DEPENDENCY AUDIT → FIVE GATES → MERGE → PULL NOW → OPERATOR ACCEPTANCE
