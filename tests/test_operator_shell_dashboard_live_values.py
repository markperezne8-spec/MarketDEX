from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_dashboard_does_not_replace_live_value_labels():
    extract = SOURCE[SOURCE.index('def _extract_mission_control'):SOURCE.index('def _install_listing_workflow_handoff')]
    assert 'QLabel(' in extract
    assert 'window.values =' not in extract
    assert 'cards_item.layout()' in extract
