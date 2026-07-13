from pathlib import Path


DOC_PATH = Path('docs/reports/inventory_age_read_api_audit.md')


def test_build701o_read_api_audit_records_current_boundaries() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'PROVIDER IMPLEMENTATION BLOCKED' in content
    assert 'InventoryAppService.get_asset_detail(asset_id)' in content
    assert "ValueError('Inventory asset not found')" in content
    assert '`quantity` and `total_cost_minor`' in content
    assert 'raw `purchase_date`, `purchase_source`, `storage_location`, and `notes`' in content
    assert 'non-`COMPLETED` asset' in content


def test_build701o_rejects_unapproved_product_link_access() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'InventoryProductLinkService' in content
    assert '`quantities(product_id)`' in content
    assert 'does not expose a read operation that accepts an Inventory `asset_id`' in content
    assert 'performs no schema initialization, write, event, audit entry, repair, or network work' in content
    assert 'no fallback may infer a product identity from asset name, type, or Inventory ID' in content
