from pathlib import Path


def test_listing_workspace_manifest_names_feature_and_gates():
    text = Path('docs/listing_workspace_build_manifest.md').read_text(encoding='utf-8')
    assert 'inventory_listing_workspace_feature.py' in text
    assert 'Inventory Listing Workspace Gate' in text
