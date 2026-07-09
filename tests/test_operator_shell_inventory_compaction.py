from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_inventory_compaction_runs_after_dashboard_extraction():
    extract = SOURCE.index('mission_control = _extract_mission_control(window)')
    compact = SOURCE.index('_compact_inventory_workspace(window)', extract)
    assert extract < compact
    assert 'window.inventory_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)' in SOURCE
