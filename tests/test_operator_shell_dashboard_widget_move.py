from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_dashboard_move_keeps_original_widgets_alive():
    extract = SOURCE[SOURCE.index('def _extract_mission_control'):SOURCE.index('def _install_listing_workflow_handoff')]
    assert 'dashboard_layout.addWidget(title_item.widget())' in extract
    assert 'dashboard_layout.addWidget(subtitle_item.widget())' in extract
    assert 'deleteLater' not in extract
