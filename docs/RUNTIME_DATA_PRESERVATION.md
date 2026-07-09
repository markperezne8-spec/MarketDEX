# Runtime Data Preservation

Release hardening treats an existing non-empty runtime database as operator data.

Startup migration does not replace that database based on inventory row counts. This protects valid databases that contain configuration, history, partial workflows, or zero completed inventory rows.

Legacy inventory seeding remains available for a missing or empty runtime database when a known legacy candidate contains completed inventory.

Focused regression coverage verifies both preservation of existing runtime content and first-run legacy seeding.
