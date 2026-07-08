from pathlib import Path


def test_launcher_installs_listing_plan_queue_after_workspace():
    source = Path('launcher.py').read_text(encoding='utf-8')
    workspace = source.index('install_inventory_listing_workspace_feature(window)')
    queue = source.index('install_inventory_listing_plan_queue_feature(window)')
    assert workspace < queue


def test_queue_is_explicitly_offline_operator_boundary():
    source = Path('docs/LISTING_PLAN_QUEUE.md').read_text(encoding='utf-8')
    assert 'offline-first' in source
    assert 'no marketplace publication occurs in this build' in source
