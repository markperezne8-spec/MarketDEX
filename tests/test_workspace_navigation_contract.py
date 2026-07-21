import os
from pathlib import Path

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QLabel,
    QMainWindow,
    QTableWidget,
    QWidget,
    QVBoxLayout,
)

from ui.inventory_workspace_focus_feature import (
    INVENTORY_WORKSPACE_FOCUS_CONTRACT,
    install_inventory_workspace_focus_feature,
)
from ui.shell_workspace_catalog import (
    INVENTORY_WORKSPACE_ID,
    LISTING_WORKFLOW_WORKSPACE_ID,
    PRICING_WORKSPACE_ID,
)
from ui.viewport_fit_feature import (
    LISTING_WORKFLOW_WIDGETS,
    PRICING_WIDGETS,
    install_viewport_fit_feature,
)
from ui.workspace_host import WorkspaceHost
from ui.workspace_registry import WorkspaceRegistry


def _window_fixture():
    window = QMainWindow()
    content = QWidget()
    panel = QWidget(content)
    panel.setLayout(QVBoxLayout())
    window.inventory_panel = panel
    window.values = {}
    window.inventory_summary = {}
    window.inventory_table = QTableWidget()
    panel.layout().addWidget(window.inventory_table)

    for attribute in LISTING_WORKFLOW_WIDGETS:
        widget = QGroupBox(attribute)
        panel.layout().addWidget(widget)
        setattr(window, attribute, widget)

    for attribute in PRICING_WIDGETS:
        widget = QLabel(attribute)
        panel.layout().addWidget(widget)
        setattr(window, attribute, widget)

    window.refresh_button = QLabel('refresh')
    panel.layout().addWidget(window.refresh_button)
    window.selected_asset_id = lambda: None
    window.show_selected = lambda: None
    window.setCentralWidget(content)
    return window


def test_existing_shell_pages_are_mounted_through_one_workspace_host():
    app = QApplication.instance() or QApplication([])
    window = _window_fixture()
    registry = WorkspaceRegistry()

    install_viewport_fit_feature(window, registry)

    assert window.workspace_registry is registry
    assert isinstance(window.workspace_host, WorkspaceHost)
    assert window.centralWidget() is window.workspace_host
    assert window.workspace_host.workspace_ids == (
        INVENTORY_WORKSPACE_ID,
        PRICING_WORKSPACE_ID,
        LISTING_WORKFLOW_WORKSPACE_ID,
    )
    assert [
        window.workspace_host.tabText(index)
        for index in range(window.workspace_host.count())
    ] == ['Inventory', 'Pricing', 'Listing Workflow']

    for workspace in registry.all():
        assert workspace.factory() is window.workspace_host.workspace_widget(
            workspace.workspace_id
        )

    window.close()


def test_top_level_workspaces_remain_available_without_inventory_selection():
    app = QApplication.instance() or QApplication([])
    window = _window_fixture()

    install_viewport_fit_feature(window)

    assert window.workspace_host.count() == 3
    assert all(
        window.workspace_host.widget(index) is not None
        for index in range(window.workspace_host.count())
    )
    assert len(window.workspace_host._navigation_buttons) == 3
    assert all(button.isEnabled() for button in window.workspace_host._navigation_buttons)
    window.close()


def test_workspace_handoffs_navigate_by_stable_workspace_identity():
    app = QApplication.instance() or QApplication([])
    window = _window_fixture()
    selected = {'asset_id': None}
    window.selected_asset_id = lambda: selected['asset_id']

    install_viewport_fit_feature(window)

    selected['asset_id'] = 'asset-1'
    window.show_selected()
    assert window.inventory_continue_to_pricing.isEnabled() is True
    assert window.inventory_continue_to_listing_workflow.isEnabled() is True

    window.inventory_continue_to_pricing.click()
    assert window.workspace_host.currentWidget() is window.workspace_host.workspace_widget(
        PRICING_WORKSPACE_ID
    )

    window.inventory_continue_to_listing_workflow.click()
    assert window.workspace_host.currentWidget() is window.workspace_host.workspace_widget(
        LISTING_WORKFLOW_WORKSPACE_ID
    )
    window.close()


def test_inventory_activation_focuses_combined_page_on_inventory_anchor():
    app = QApplication.instance() or QApplication([])
    window = _window_fixture()
    mission_control_stub = QLabel('Mission Control content')
    mission_control_stub.setFixedHeight(1200)
    window.inventory_panel.layout().insertWidget(0, mission_control_stub)

    install_viewport_fit_feature(window)
    install_inventory_workspace_focus_feature(window)
    window.resize(1000, 600)
    window.show()
    app.processEvents()

    window.workspace_host.activate(PRICING_WORKSPACE_ID)
    window.workspace_host.activate(INVENTORY_WORKSPACE_ID)
    app.processEvents()
    app.processEvents()

    scroll = window.marketdex_workspace_scroll
    content = scroll.widget()
    anchor = window.inventory_workspace_anchor
    target = anchor.mapTo(content, QPoint(0, 0)).y()
    expected = max(
        scroll.verticalScrollBar().minimum(),
        min(target, scroll.verticalScrollBar().maximum()),
    )

    assert anchor.objectName() == 'marketdexInventoryWorkspaceAnchor'
    assert anchor.property('visualContract') == INVENTORY_WORKSPACE_FOCUS_CONTRACT
    assert scroll.verticalScrollBar().value() == expected
    assert scroll.verticalScrollBar().value() > 0
    window.close()


def test_shell_publishes_legacy_tab_aliases_without_duplicate_navigation_state():
    app = QApplication.instance() or QApplication([])
    window = _window_fixture()

    install_viewport_fit_feature(window)

    assert window.marketdex_workspace_tabs is window.workspace_host
    assert window.marketdex_workspace_indexes == window.workspace_host.workspace_indexes
    assert window.marketdex_workspace_scroll.widget() is not None
    assert window.marketdex_pricing_workspace_scroll.widget() is not None
    assert window.marketdex_listing_workflow_scroll.widget() is not None
    window.close()


def test_pricing_workspace_uses_canonical_dark_theme_contract():
    app = QApplication.instance() or QApplication([])
    window = _window_fixture()

    install_viewport_fit_feature(window)

    pricing = window.workspace_host.workspace_widget(PRICING_WORKSPACE_ID)
    content = window.marketdex_pricing_workspace_scroll.widget()
    assert pricing is not None
    assert content.objectName() == 'marketdexPricingWorkspace'
    assert window.inventory_listing_workflow_handoff.objectName() == (
        'workspaceHandoffCard'
    )
    assert window.inventory_listing_workflow_guidance.objectName() == (
        'workspaceHandoffGuidance'
    )

    source = Path(__file__).resolve().parents[1].joinpath(
        'ui', 'viewport_fit_feature.py'
    ).read_text(encoding='utf-8')
    for legacy_color in ('#ffffff', '#d7dee8', '#0f172a', '#475569', '#64748b'):
        assert legacy_color not in source
    window.close()


def test_listing_workspace_uses_canonical_dark_theme_contract():
    app = QApplication.instance() or QApplication([])
    window = _window_fixture()

    install_viewport_fit_feature(window)

    listing = window.workspace_host.workspace_widget(
        LISTING_WORKFLOW_WORKSPACE_ID
    )
    content = window.marketdex_listing_workflow_scroll.widget()
    assert listing is not None
    assert content.objectName() == 'marketdexListingWorkspace'

    theme = Path(__file__).resolve().parents[1].joinpath(
        'ui', 'design_system', 'qt_theme.py'
    ).read_text(encoding='utf-8')
    assert 'QWidget#marketdexListingWorkspace QGroupBox' in theme
    assert 'QWidget#marketdexListingWorkspace QGroupBox::title' in theme
    assert 'QWidget#marketdexListingWorkspace QLabel' in theme
    window.close()
