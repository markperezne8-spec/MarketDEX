# Workspace Tab Access Traceability

Operator report: Pricing and Listing Workflow pages could not be opened.

Root cause: `ui/viewport_fit_feature.py` tied tab enabled state to inventory selection and redirected non-Inventory views back to Inventory when no asset was selected.

Fix: remove tab enable/disable and forced redirect behavior. Preserve selection gating only on workflow handoff buttons.

Test: `tests/test_workspace_tab_access.py`.
Gate: `Workspace Tab Access Gate`.
