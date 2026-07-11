import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QLabel,
    QMainWindow,
    QTableWidget,
    QWidget,
    QVBoxLayout,
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
