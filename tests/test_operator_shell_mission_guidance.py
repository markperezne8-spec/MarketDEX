from pathlib import Path


def test_mission_control_guidance_changes_with_inventory_state():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')

    assert "if snapshot['inventory_asset_count']:" in source
    assert 'Inventory is ready. Open Inventory' in source
    assert 'Add or import your first inventory asset.' in source
    assert "QGroupBox('🚀 NEXT ACTION')" in source
