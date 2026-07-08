from pathlib import Path


def test_launcher_installs_preparation_after_execution_readiness():
    source = Path('launcher.py').read_text(encoding='utf-8')
    readiness = source.index('install_inventory_listing_execution_readiness_feature(window)')
    preparation = source.index('install_inventory_marketplace_listing_preparation_feature(window)')
    assert readiness < preparation


def test_preparation_preserves_offline_publication_boundary():
    source = Path('docs/MARKETPLACE_LISTING_PREPARATION.md').read_text(encoding='utf-8')
    assert 'offline listing package' in source
    assert 'does not publish, submit, or modify a marketplace listing' in source
