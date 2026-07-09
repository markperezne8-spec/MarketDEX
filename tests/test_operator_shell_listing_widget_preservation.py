from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_existing_listing_workflow_stages_remain_in_shell():
    for name in (
        'inventory_listing_workspace',
        'inventory_listing_plan_queue',
        'inventory_listing_execution_readiness',
        'inventory_marketplace_listing_preparation',
        'inventory_marketplace_listing_package_review',
        'inventory_completed_listing_package_queue',
        'inventory_listing_execution_history',
        'inventory_sale_completion',
    ):
        assert name in SOURCE
