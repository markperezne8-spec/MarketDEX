from pathlib import Path


def test_launcher_installs_completed_queue_after_package_review():
    source = Path('launcher.py').read_text(encoding='utf-8')
    review = source.index('install_inventory_marketplace_listing_package_review_feature(window)')
    queue = source.index('install_inventory_completed_listing_package_queue_feature(window)')
    assert review < queue


def test_completed_queue_preserves_offline_operator_authority():
    source = Path('docs/COMPLETED_LISTING_PACKAGE_QUEUE.md').read_text(encoding='utf-8')
    assert 'operator handoff' in source.lower()
    assert 'does not publish, submit, synchronize, or modify marketplace state' in source
    assert 'sale completion remains separate' in source.lower()
