from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_listing_handoff_remains_exposed_for_existing_ui_contracts():
    assert 'window.inventory_listing_workflow_handoff = handoff' in SOURCE
    assert 'window.inventory_continue_to_listing_workflow = continue_button' in SOURCE
