from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_mission_control_has_desktop_dashboard_spacing():
    extract = SOURCE[SOURCE.index('def _extract_mission_control'):SOURCE.index('def _install_listing_workflow_handoff')]
    assert 'setContentsMargins(24, 20, 24, 20)' in extract
    assert 'setSpacing(10)' in extract
