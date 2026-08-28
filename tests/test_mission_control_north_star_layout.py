from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_WINDOW = ROOT / "ui" / "main_window.py"
WORKSPACE_HOST = ROOT / "ui" / "workspace_host.py"
HEADER_STATUS_BAND = ROOT / "ui" / "header_status_band.py"
OPERATIONAL_STATUS_STRIP = ROOT / "ui" / "operational_status_strip.py"
NEXT_STEPS_PANEL = ROOT / "ui" / "next_steps_panel.py"


def test_mission_control_uses_a_three_column_north_star_command_deck():
    source = MAIN_WINDOW.read_text(encoding="utf-8")

    assert "MISSION_CONTROL_TWO_COLUMN_MINIMUM_WIDTH = 1200" in source
    assert "(self.todays_top3_panel,4,0,1,1)" in source
    assert "(self.capital_health_panel,4,1,1,1)" in source
    assert "(self.opportunity_risk_panel,4,2,1,1)" in source
    assert "(self.business_scoreboard_panel,5,0,1,3)" in source
    assert "(self.dashboard_grid_shell,6,0,1,3)" in source
    assert "self.mission_control_grid.setColumnStretch(1,7)" not in source
    assert "self.health_status_card.set_tone(NorthStarPanelTone.RISK)" in source
    assert "self.operational_status_strip.set_tone(NorthStarPanelTone.OPPORTUNITY)" in source
    assert "self.next_steps_panel.set_tone(NorthStarPanelTone.SCOREBOARD)" in source
    assert "self.todays_top3_panel.set_tone(NorthStarPanelTone.OPPORTUNITY)" in source
    assert "self.capital_health_panel.set_tone(NorthStarPanelTone.SCOREBOARD)" in source
    assert "self.opportunity_risk_panel.set_tone(NorthStarPanelTone.RISK)" in source
    assert "self.business_scoreboard_panel.set_tone(NorthStarPanelTone.SCOREBOARD)" in source


def test_dashboard_grid_kpis_use_presentation_only_category_cues():
    source = MAIN_WINDOW.read_text(encoding="utf-8")
    theme_source = (ROOT / "ui" / "design_system" / "qt_theme.py").read_text(encoding="utf-8")

    assert "for index,(label,key,metric_group) in enumerate(cards)" in source
    assert "MarketDEXKpiCard(label,'--',dashboard_role='existing-kpi',metric_group=metric_group)" in source
    assert "dashboard_role: str | None = None" in (ROOT / "ui" / "design_system" / "widgets.py").read_text(encoding="utf-8")
    assert "('📦 Inventory Units','inventory_units','inventory')" in source
    assert "('💰 Inventory Cost','inventory_cost_minor','commercial')" in source
    assert "('🛡️ Verified Audits','verified_audits','governance')" in source
    assert '[dashboardMetricGroup="inventory"]' in theme_source
    assert '[dashboardMetricGroup="commercial"]' in theme_source
    assert '[dashboardMetricGroup="governance"]' in theme_source


def test_nested_readiness_rows_wrap_without_horizontal_overflow():
    header_source = HEADER_STATUS_BAND.read_text(encoding="utf-8")
    operational_source = OPERATIONAL_STATUS_STRIP.read_text(encoding="utf-8")
    next_steps_source = NEXT_STEPS_PANEL.read_text(encoding="utf-8")

    assert "QGridLayout(self.slot_row)" in header_source
    assert "self.slot_layout.addWidget(card, index // 3, index % 3)" in header_source
    assert "QHBoxLayout(self.slot_row)" not in header_source
    assert "QGridLayout(self.group_row)" in operational_source
    assert "self.group_layout.addWidget(group_widget, index // 2, index % 2)" in operational_source
    assert "QHBoxLayout(self.group_row)" not in operational_source
    assert "QGridLayout(self.group_row)" in next_steps_source
    assert "self.group_layout.addWidget(group_widget, index // 2, index % 2)" in next_steps_source
    assert "QHBoxLayout(self.group_row)" not in next_steps_source


def test_north_star_shell_has_layered_dark_mode_status_hierarchy():
    source = WORKSPACE_HOST.read_text(encoding="utf-8")

    assert "qlineargradient" in source
    assert "QFrame#marketdexGlobalHeader" in source
    assert "QLabel#marketdexGlobalStatus" in source
    assert "border: {border['standard']}px solid {color(ColorRole.POSITIVE)};" in source
