import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication, QGroupBox, QLabel, QMainWindow, QSizePolicy, QTableWidget, QTabWidget, QWidget, QVBoxLayout

from ui.viewport_fit_feature import LISTING_WORKFLOW_WIDGETS, SALES_WORKFLOW_WIDGETS, install_viewport_fit_feature


class _Service:
    def snapshot(self):
        return {
            'inventory_units': 12,
            'inventory_asset_count': 3,
            'inventory_cost_minor': 12500,
            'completed_sales': 4,
            'revenue_minor': 22000,
            'profit_minor': 9500,
            'verified_audits': 7,
            'authority_events': 9,
        }


def _window_fixture():
    window = QMainWindow()
    content = QWidget()
    panel = QWidget(content)
    panel.setLayout(QVBoxLayout())
    window.inventory_panel = panel
    window.values = {}
    for key in ('units', 'assets'):
        box = QGroupBox(key)
        box.setLayout(QVBoxLayout())
        value = QLabel('0')
        box.layout().addWidget(value)
        panel.layout().addWidget(box)
        window.values[key] = value
    window.inventory_summary = {}
    for key in ('asset_count', 'total_units', 'total_cost_minor'):
        box = QGroupBox(key)
        box.setLayout(QVBoxLayout())
        value = QLabel('0')
        box.layout().addWidget(value)
        panel.layout().addWidget(box)
        window.inventory_summary[key] = value
    window.inventory_table = QTableWidget()
    panel.layout().addWidget(window.inventory_table)
    for attribute in LISTING_WORKFLOW_WIDGETS + SALES_WORKFLOW_WIDGETS:
        widget = QGroupBox(attribute)
        panel.layout().addWidget(widget)
        setattr(window, attribute, widget)
    window.service = _Service()
    window._money = lambda value: f'${value / 100:,.2f}'
    window.refresh = lambda: None
    window.setCentralWidget(content)
    return window, content, panel


def test_viewport_fit_recomposes_business_flow_into_five_workspaces():
    app = QApplication.instance() or QApplication([])
    window, content, panel = _window_fixture()
    install_viewport_fit_feature(window)

    tabs = window.centralWidget()
    assert isinstance(tabs, QTabWidget)
    assert [tabs.tabText(index) for index in range(tabs.count())] == [
        'Mission Control',
        'Inventory',
        'Pricing',
        'Listings',
        'Sales',
    ]
    assert window.marketdex_workspace_scroll.widget() is content
    for attribute in LISTING_WORKFLOW_WIDGETS + SALES_WORKFLOW_WIDGETS:
        assert getattr(window, attribute).parentWidget() is not panel
    assert window.marketdex_mission_values['inventory_units'].text() == '12'
    assert window.marketdex_mission_values['inventory_cost_minor'].text() == '$125.00'
    assert 'Inventory is ready' in window.marketdex_mission_guidance.text()
    window.close()


def test_viewport_fit_hides_legacy_metrics_and_gives_table_expandable_height():
    app = QApplication.instance() or QApplication([])
    window, _, _ = _window_fixture()
    install_viewport_fit_feature(window)

    for value in window.values.values():
        assert value.parentWidget().isHidden()
    for value in window.inventory_summary.values():
        assert value.parentWidget().maximumHeight() == 58
    assert window.inventory_table.minimumHeight() == 120
    assert window.inventory_table.sizePolicy().verticalPolicy() == QSizePolicy.Expanding
    window.close()


def test_operator_handoffs_follow_inventory_pricing_listings_flow():
    app = QApplication.instance() or QApplication([])
    window, _, _ = _window_fixture()
    install_viewport_fit_feature(window)

    tabs = window.marketdex_workspace_tabs
    window.inventory_continue_to_listing_workflow.click()
    assert tabs.currentIndex() == 2
    window.marketdex_pricing_listings_button.click()
    assert tabs.currentIndex() == 3
    window.close()
