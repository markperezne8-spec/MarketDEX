from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_mission_control_explains_workspace_purpose():
    assert 'Your business at a glance.' in SOURCE
    assert 'dedicated workspaces' in SOURCE
    assert 'dashboard_layout.addStretch(1)' in SOURCE
