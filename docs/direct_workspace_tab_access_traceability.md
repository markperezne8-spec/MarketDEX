# Traceability — Direct Workspace Tab Access

Live operator report: Pricing and Listing Workflow pages could not be opened.

Root cause: `ui/viewport_fit_feature.py` disabled tab indexes 1 and 2 when no inventory asset was selected and redirected non-Inventory tabs back to Inventory.

Repair: remove tab enable/disable and forced redirect from selection handling; retain selection authority on guided Continue buttons.

Verification: `tests/test_viewport_fit_feature.py` asserts both downstream tabs are enabled without selection and remain open after selection clears.
