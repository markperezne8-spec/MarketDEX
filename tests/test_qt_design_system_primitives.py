from pathlib import Path

from PySide6.QtWidgets import QApplication

from ui.design_system.qt_theme import build_marketdex_qss
from ui.design_system.tokens import (
    ColorRole,
    NorthStarPanelTone,
    build_visual_north_star_tokens,
)
from ui.design_system.widgets import (
    MarketDEXDashboardPanel,
    MarketDEXKpiCard,
    MarketDEXStatePanel,
    MarketDEXStatusBadge,
    MarketDEXWorkspaceHeader,
)


def _application():
    return QApplication.instance() or QApplication([])


def test_qt_theme_is_generated_from_semantic_tokens():
    tokens = build_visual_north_star_tokens()
    qss = build_marketdex_qss(tokens)

    for selector in (
        'QFrame#marketdexWorkspaceHeader',
        'QFrame#marketdexDashboardPanel',
        'QFrame#marketdexKpiCard',
        'QLabel#marketdexStatusBadge',
        f'QFrame#marketdexDashboardPanel[northStarTone="{NorthStarPanelTone.OPPORTUNITY.value}"]',
        f'QFrame#marketdexDashboardPanel[northStarTone="{NorthStarPanelTone.RISK.value}"]',
        'QPushButton#marketdexPrimaryButton',
        'QTableView, QTableWidget',
    ):
        assert selector in qss

    for role in (
        ColorRole.APP_BACKGROUND,
        ColorRole.SURFACE_PRIMARY,
        ColorRole.BORDER_STRONG,
        ColorRole.TEXT_PRIMARY,
        ColorRole.POSITIVE,
        ColorRole.WARNING,
        ColorRole.NEGATIVE,
        ColorRole.FOCUS_RING,
    ):
        assert tokens.color(role) in qss


def test_dashboard_panel_exposes_read_only_north_star_tone_property():
    _application()
    panel = MarketDEXDashboardPanel(
        'Opportunity + Risk',
        'Read-only shell',
        None,
        tone=NorthStarPanelTone.OPPORTUNITY,
    )

    assert panel.property('northStarTone') == NorthStarPanelTone.OPPORTUNITY.value
    assert panel.header_actions.count() == 0

    panel.set_tone(NorthStarPanelTone.RISK)

    assert panel.property('northStarTone') == NorthStarPanelTone.RISK.value


def test_first_qt_component_types_are_available_without_business_dependencies():
    component_types = (
        MarketDEXWorkspaceHeader,
        MarketDEXKpiCard,
        MarketDEXStatusBadge,
        MarketDEXDashboardPanel,
        MarketDEXStatePanel,
    )

    assert len({component.__name__ for component in component_types}) == len(component_types)

    source = Path('ui/design_system/widgets.py').read_text(encoding='utf-8')
    for prohibited in (
        'sqlite3',
        'repositories.',
        'services.',
        'InventoryAppService',
        'MissionControlService',
    ):
        assert prohibited not in source


def test_theme_adapter_remains_business_and_database_independent():
    source = Path('ui/design_system/qt_theme.py').read_text(encoding='utf-8')

    assert 'from ui.design_system.tokens import' in source
    assert 'sqlite3' not in source
    assert 'services.' not in source
    assert 'repositories.' not in source
