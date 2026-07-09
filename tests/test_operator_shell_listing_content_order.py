from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_listing_stage_attributes_keep_existing_business_order():
    names = [
        'inventory_listing_workspace',
        'inventory_listing_plan_queue',
        'inventory_listing_execution_readiness',
        'inventory_marketplace_listing_preparation',
        'inventory_marketplace_listing_package_review',
        'inventory_completed_listing_package_queue',
        'inventory_listing_execution_history',
        'inventory_sale_completion',
    ]
    positions = [SOURCE.index(f"'{name}'") for name in names]
    assert positions == sorted(positions)
