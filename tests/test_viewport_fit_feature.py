import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication, QGroupBox, QLabel, QMainWindow, QSizePolicy, QTableWidget, QTabWidget, QWidget, QVBoxLayout
from ui.viewport_fit_feature import install_viewport_fit_feature, LISTING_WORKFLOW_WIDGETS


def _window_fixture():
    window = QMainWindow()
    content = QWidget(); panel = QWidget(content); panel.setLayout(QVBoxLayout())
    window.inventory_panel = panel
    window.values = {}
    for key in ('units', 'assets'):
        box = QGroupBox(key); box.setLayout(QVBoxLayout()); value = QLabel('0'); box.layout().addWidget(value); panel.layout().addWidget(box); window.values[key] = value
    window.inventory_summary = {}
    for key in ('asset_count', 'total_units', 'total_cost_minor'):
        box = QGroupBox(key); box.setLayout(QVBoxLayout()); value = QLabel('0'); box.layout().addWidget(value); panel.layout().addWidget(box); window.inventory_summary[key] = value
    window.inventory_table = QTableWidget()
    panel.layout().addWidget(window.inventory_table)
    for attribute in LISTING_WORKFLOW_WIDGETS:
        widget = QGroupBox(attribute)
        panel.layout().addWidget(widget)
        setattr(window, attribute, widget)
    for attribute in ('inventory_cost_summary', 'inventory_sale_readiness', 'inventory_profit_summary', 'inventory_price_guidance'):
        widget = QLabel(attribute)
        panel.layout().addWidget(widget)
        setattr(window, attribute, widget)
    window.refresh_button = QLabel('refresh'); panel.layout().addWidget(window.refresh_button)
    window.selected_asset_id = lambda: None
    window.show_selected = lambda: None
    window.setCentralWidget(content)
    return window, content, panel


def test_viewport_fit_splits_inventory_pricing_and_listing_workflow_into_tabs():
    app = QApplication.instance() or QApplication([])
    window, content, panel = _window_fixture()
    install_viewport_fit_feature(window)
    assert isinstance(window.centralWidget(), QTabWidget)
    assert [window.centralWidget().tabText(index) for index in range(window.centralWidget().count())] == ['Inventory', 'Pricing', 'Listing Workflow']
    assert window.marketdex_workspace_scroll.widget() is content
    for attribute in LISTING_WORKFLOW_WIDGETS:
        assert getattr(window, attribute).parentWidget() is not panel
    assert window.inventory_continue_to_pricing.isEnabled() is False
    assert window.inventory_continue_to_listing_workflow.isEnabled() is False
    assert panel.layout().indexOf(window.inventory_pricing_handoff) < panel.layout().indexOf(window.inventory_table)
    assert window.marketdex_pricing_workspace_scroll.widget().layout().indexOf(window.inventory_listing_workflow_handoff) < window.marketdex_pricing_workspace_scroll.widget().layout().indexOf(window.inventory_cost_summary)
    window.close()


def test_inventory_and_pricing_handoffs_follow_operator_flow():
    app = QApplication.instance() or QApplication([])
    window, _, _ = _window_fixture()
    selected = {'asset_id': None}
    window.selected_asset_id = lambda: selected['asset_id']
    install_viewport_fit_feature(window)
    tabs = window.marketdex_workspace_tabs
    selected['asset_id'] = 'asset-1'; window.show_selected()
    assert window.inventory_continue_to_pricing.isEnabled() is True
    assert window.inventory_continue_to_listing_workflow.isEnabled() is True
    assert window.inventory_pricing_guidance.text().startswith('Asset selected.')
    assert window.inventory_listing_workflow_guidance.text().startswith('Asset selected.')
    window.inventory_continue_to_pricing.click()
    assert tabs.currentIndex() == 1
    window.inventory_continue_to_listing_workflow.click()
    assert tabs.currentIndex() == 2
    window.close()


def test_viewport_fit_compacts_metrics_and_gives_table_expandable_height():
    app = QApplication.instance() or QApplication([])
    window, _, _ = _window_fixture()
    install_viewport_fit_feature(window)
    for value in window.values.values():
        assert value.parentWidget().maximumHeight() == 64
    for value in window.inventory_summary.values():
        assert value.parentWidget().maximumHeight() == 58
    assert window.inventory_table.minimumHeight() == 120
    assert window.inventory_table.sizePolicy().verticalPolicy() == QSizePolicy.Expanding
    window.close()
