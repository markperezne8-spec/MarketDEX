import os
from pathlib import Path

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication, QGroupBox, QLabel, QMainWindow, QTableWidget, QWidget, QVBoxLayout

from ui.viewport_fit_feature import LISTING_WORKFLOW_WIDGETS, PRICING_WIDGETS, install_viewport_fit_feature
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


def test_top_level_workspace_tabs_are_not_selection_locked():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')
    assert 'tabs.setTabEnabled(1, selected)' not in source
    assert 'tabs.setTabEnabled(2, selected)' not in source
    assert 'if not selected and tabs.currentIndex() != 0:' not in source


def test_top_level_workspaces_are_registered_through_the_canonical_registry():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')

    assert "('inventory', 'Inventory', 10)" in source
    assert "('pricing', 'Pricing', 20)" in source
    assert "('listing-workflow', 'Listing Workflow', 30)" in source
    assert 'for workspace in workspace_registry.all():' in source
    assert 'workspace_indexes[workspace.workspace_id] = tabs.addTab(page, workspace.title)' in source
    assert "tabs.addTab(inventory_page, 'Inventory')" not in source
    assert "tabs.addTab(pricing_page, 'Pricing')" not in source
    assert "tabs.addTab(listing_page, 'Listing Workflow')" not in source


def test_existing_shell_pages_are_registered_as_real_workspace_widgets():
    app = QApplication.instance() or QApplication([])
    window = _window_fixture()
    registry = WorkspaceRegistry()

    install_viewport_fit_feature(window, registry)

    assert window.workspace_registry is registry
    assert [workspace.workspace_id for workspace in registry.all()] == [
        'inventory',
        'pricing',
        'listing-workflow',
    ]
    for workspace in registry.all():
        index = window.marketdex_workspace_indexes[workspace.workspace_id]
        assert window.marketdex_workspace_tabs.tabText(index) == workspace.title
        assert workspace.factory() is window.marketdex_workspace_tabs.widget(index)
    window.close()


def test_workspace_handoffs_navigate_by_stable_workspace_identity():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')

    assert "_activate_workspace(window, 'pricing')" in source
    assert "_activate_workspace(window, 'listing-workflow')" in source
    assert 'tabs.setCurrentIndex(1)' not in source
    assert 'tabs.setCurrentIndex(2)' not in source
