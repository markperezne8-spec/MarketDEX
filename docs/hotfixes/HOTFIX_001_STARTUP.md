# MarketDEX Startup Hotfix 001

## Issue
ModuleNotFoundError:
app.ui.dialogs.edit_inventory_dialog

## Root Cause
The dialogs package was missing an __init__.py file in this project structure.

## Fix
- Added app/ui/dialogs/__init__.py

## Verification Checklist
- [ ] launcher.py starts
- [ ] QApplication created
- [ ] AppShell loads
- [ ] Inventory page imports successfully
- [ ] Main window opens

Engineering Rule:
Prefer the smallest verified fix before making architectural changes.
