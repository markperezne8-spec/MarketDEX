from pathlib import Path


def test_launcher_installs_execution_readiness_after_queue():
    source = Path('launcher.py').read_text(encoding='utf-8')
    queue = source.index('install_inventory_listing_plan_queue_feature(window)')
    readiness = source.index('install_inventory_listing_execution_readiness_feature(window)')
    assert queue < readiness


def test_execution_readiness_preserves_offline_publication_boundary():
    source = Path('docs/LISTING_EXECUTION_READINESS.md').read_text(encoding='utf-8')
    assert 'offline operator gate' in source
    assert 'does not publish, submit, or modify a marketplace listing' in source
