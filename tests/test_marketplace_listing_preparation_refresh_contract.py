from pathlib import Path


def test_listing_preparation_refreshes_on_selection_and_plan_save():
    source = Path('ui/inventory_marketplace_listing_preparation_feature.py').read_text(encoding='utf-8')
    assert 'itemSelectionChanged.connect(window.show_selected)' in source
    assert 'window.inventory_save_listing_plan.clicked.connect(refresh_preparation)' in source
    assert 'window.refresh_marketplace_listing_preparation = refresh_preparation' in source
