# Build 504 — Stale Cross-Check Authority Repair

Issue: #133

A stored allocation-group cross-check is authoritative only while it still represents the complete current append-only allocation group. The repository fails closed when evidence was appended after the latest cross-check, an allocation amount is unknown, or the current group total differs from the stored cross-check total.

This preserves the existing Builds 498–503 architecture and prevents stale cross-check evidence from granting Build 501 `LOCK ELIGIBLE`, Build 503 `LOCKED`, or sale-level settlement attribution readiness authority.
