import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication, QGroupBox, QLabel, QMainWindow, QSizePolicy, QTableWidget, QTabWidget, QWidget, QVBoxLayout
from ui.viewport_fit_feature import install_viewport_fit_feature, LISTING_WORKFLOW_WIDGETS, SALES_WORKFLOW_WIDGETS


class _SnapshotService:
    def snapshot(self):
        return {
            'inventory_units': 0,
            'inventory_asset_count': 0,
            'inventory_cost_minor': 0,
            'completed_sales': 0,
            'revenue_minor': 0,
            'profit_minor': 0,
            'verified_audits': 0,
            'authority_events': 0,
        }


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
    for attribute in LISTING_WORKFLOW_WIDGETS + SALES_WORKFLOW_WIDGETS:
        widget = QGroupBox(attribute)
        panel.layout().addWidget(widget)
        setattr(window, attribute, widget)
    window.refresh_button = None
    window.service = _SnapshotService()
    window.refresh = lambda: None
    window._money = lambda minor: f'${minor / 100:,.2f}'
    window.setCentralWidget(content)
    return window, content, panel


def test_viewport_fit_splits_operator_workspaces_into_tabs():
    app = QApplication.instance() or QApplication([])
    window, content, panel = _window_fixture()
    install_viewport_fit_feature(window)
    assert isinstance(window.centralWidget(), QTabWidget)
    assert window.centralWidget().count() == 5
    assert [window.centralWidget().tabText(index) for index in range(5)] == ['Mission Control', 'Inventory', 'Pricing', 'Listings', 'Sales']
    assert window.marketdex_workspace_scroll.widget() is content
    for attribute in LISTING_WORKFLOW_WIDGETS + SALES_WORKFLOW_WIDGETS:
        assert getattr(window, attribute).parentWidget() is not panel
    window.close()


def test_viewport_fit_compacts_metrics_and_gives_table_expandable_height():
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
