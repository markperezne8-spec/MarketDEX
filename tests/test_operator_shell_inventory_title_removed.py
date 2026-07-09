from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_dashboard_header_and_cards_are_removed_from_inventory_panel_before_tabs_are_built():
    extract_call = SOURCE.index('mission_control = _extract_mission_control(window)')
    tabs_build = SOURCE.index('tabs = QTabWidget(window)')
    assert extract_call < tabs_build
    assert SOURCE.count('panel_layout.takeAt(0)') == 3
