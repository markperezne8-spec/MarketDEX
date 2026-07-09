from pathlib import Path


def test_operator_shell_preserves_complete_listing_widget_set():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')

    for widget in (
        'inventory_listing_workspace',
        'inventory_listing_plan_queue',
        'inventory_listing_execution_readiness',
        'inventory_marketplace_listing_preparation',
        'inventory_marketplace_listing_package_review',
        'inventory_completed_listing_package_queue',
        'inventory_listing_execution_history',
        'inventory_sale_completion',
    ):
        assert f"'{widget}'" in source
