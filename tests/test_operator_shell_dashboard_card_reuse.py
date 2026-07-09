from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_dashboard_reuses_existing_live_snapshot_cards():
    assert 'title_item = panel_layout.takeAt(0)' in SOURCE
    assert 'subtitle_item = panel_layout.takeAt(0)' in SOURCE
    assert 'cards_item = panel_layout.takeAt(0)' in SOURCE
    assert 'dashboard_layout.addLayout(cards_item.layout())' in SOURCE
    assert 'window.values' in SOURCE
