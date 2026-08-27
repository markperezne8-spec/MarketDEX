from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_WINDOW = ROOT / "ui" / "main_window.py"
WORKSPACE_HOST = ROOT / "ui" / "workspace_host.py"


def test_mission_control_uses_a_three_column_north_star_command_deck():
    source = MAIN_WINDOW.read_text(encoding="utf-8")

    assert "MISSION_CONTROL_TWO_COLUMN_MINIMUM_WIDTH = 1200" in source
    assert "(self.todays_top3_panel,4,0,1,1)" in source
    assert "(self.capital_health_panel,4,1,1,1)" in source
    assert "(self.opportunity_risk_panel,4,2,1,1)" in source
    assert "(self.dashboard_grid_shell,6,0,1,3)" in source
    assert "self.mission_control_grid.setColumnStretch(1,7)" not in source


def test_north_star_shell_has_layered_dark_mode_status_hierarchy():
    source = WORKSPACE_HOST.read_text(encoding="utf-8")

    assert "qlineargradient" in source
    assert "QFrame#marketdexGlobalHeader" in source
    assert "QLabel#marketdexGlobalStatus" in source
    assert "border: {border['standard']}px solid {color(ColorRole.POSITIVE)};" in source
