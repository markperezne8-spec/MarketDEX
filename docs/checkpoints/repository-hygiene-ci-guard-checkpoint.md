# Repository Hygiene and CI Guard Checkpoint

**Status:** Checkpoint synchronization active
**Canonical branch:** `main`
**Source of truth:** GitHub repository `markperezne8-spec/MarketDEX`
**Issue:** #553
**Parent merge:** `1d837b6355b232770d27c12d7cbf3dc1024f14b3`

## Summary

This checkpoint records the completed GitHub-first repository inspection, hygiene, and CI guard sequence after the M1.20A checkpoint synchronization.

The sequence was governance and repository-maintenance work only. It introduced no runtime behavior, UI behavior, business logic, persistence, networking, providers, alerts, notifications, automation, or business-state mutation.

## Completed builds

| Build | Issue | PR | CI run | Head SHA | Merge SHA | Result |
|---|---:|---:|---:|---|---|---|
| Canonical runtime authority guard | #545 | #546 | #811 | `4e14fc5423586813b479b5138d9201125aeb2bbd` | `ccf7fc48d45b74cacc8093c6bf5f6d1a12b878b8` | Locked launcher, composition root, UI import path, and packaging entrypoint against legacy runtime drift. |
| Local scratch-folder ignore rules | #547 | #548 | #813 | `201cb071eb2e3652c27c9239788d64cd4f247e69` | `90bd416228e35991b9a019ed62dfdcb00f9a042f` | Ignored local `.codex-audit-pytest*/` and `.codex-pytest-tmp*/` folders. |
| Python cache key stabilization | #549 | #550 | #815 | `3e7ddd93e97f63d9560ac8476f28f29e04dd829e` | `601f61556be927c64fd08a6c214da90b48971e30` | Added explicit `cache-dependency-path` values for Python dependency caching. |
| CI workflow gate inventory guard | #551 | #552 | #817 | `4785b5234d65d303d25e87831ab96df302b49f0f` | `1d837b6355b232770d27c12d7cbf3dc1024f14b3` | Added `tests/test_ci_workflow_contract.py` and ran it in Desktop Build. |

## Locked decisions

- The canonical runtime remains root `launcher.py`, root `composition/`, root `ui/`, and root `services/`.
- Legacy `app/ui`, `app/services`, `app/database`, and `app/repositories` remain explicitly noncanonical until separately reviewed, migrated, or retired.
- Local Codex/Pytest audit scratch folders are temporary local workspaces, not repository source.
- CI acceleration may improve caching, but it must not remove required jobs or weaken Desktop Build, packaged runtime verification, installer build, or installed runtime verification.
- Workflow changes must remain GitHub-first: issue -> branch -> draft PR -> CI -> ready -> squash-merge.

## Pull and visual status

- Pull required locally: **YES when Mark is back at the PC**.
- Pull instruction: GitHub Desktop -> `main` -> Fetch origin -> Pull origin.
- Visual check required: **NO**.
- Codex used: **YES, explicitly authorized by Mark in this workflow**.

## Next gate

After local pull when practical, the next build may proceed from synchronized `main`.

Preferred next engineering movement: continue repository inspection findings through small, guarded slices. Do not delete the legacy `app/` tree, broaden migration scope, add dependencies, weaken CI, or introduce runtime/UI behavior without a dedicated issue and acceptance gate.
