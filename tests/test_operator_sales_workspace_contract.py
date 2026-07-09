from pathlib import Path

from ui.viewport_fit_feature import LISTING_WORKFLOW_WIDGETS, SALES_WORKFLOW_WIDGETS


def test_sales_authority_is_separated_from_listing_workspace():
    assert SALES_WORKFLOW_WIDGETS == (
        'inventory_listing_execution_history',
        'inventory_sale_completion',
    )
    assert set(SALES_WORKFLOW_WIDGETS).isdisjoint(LISTING_WORKFLOW_WIDGETS)


def test_operator_shell_exposes_dedicated_listings_and_sales_tabs():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')
    assert "tabs.addTab(listing_page, 'Listings')" in source
    assert "tabs.addTab(sales_page, 'Sales')" in source
    assert 'window.marketdex_sales_workflow_scroll = sales_scroll' in source
