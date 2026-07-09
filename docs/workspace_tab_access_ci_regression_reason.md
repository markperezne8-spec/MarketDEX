# Workspace Tab Access CI Regression Reason

The runtime behavior changed from selection-locked tabs to direct navigation, but `tests/test_viewport_fit_feature.py` still asserted disabled tabs and forced return to Inventory. Those assertions correctly failed against the repaired implementation and have now been replaced with the intended navigation contract.
