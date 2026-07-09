# Workspace Tab Access Fix

Pricing and Listing Workflow are top-level operator workspaces and must remain directly navigable from their tabs.

Inventory selection still controls workflow action buttons because those actions require an asset context. It must not disable or redirect away from the Pricing or Listing Workflow tabs.

Regression coverage: `tests/test_workspace_tab_access.py`.
