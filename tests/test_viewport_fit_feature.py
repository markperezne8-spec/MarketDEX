import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGroupBox, QTabWidget
from ui.viewport_fit_feature import install_viewport_fit_feature, LISTING_WORKFLOW_WIDGETS


def test_viewport_fit_splits_inventory_and_listing_workflow_into_tabs():
    app = QApplication.instance() or QApplication([])
    window = QMainWindow()
    content = QWidget(); panel = QWidget(content); panel.setLayout(QVBoxLayout())
    window.inventory_panel = panel
    for attribute in LISTING_WORKFLOW_WIDGETS:
        widget = QGroupBox(attribute)
        panel.layout().addWidget(widget)
        setattr(window, attribute, widget)
    window.setCentralWidget(content)
    install_viewport_fit_feature(window)
    assert isinstance(window.centralWidget(), QTabWidget)
    assert window.centralWidget().count() == 2
    assert window.centralWidget().tabText(0) == 'Inventory & Pricing'
    assert window.centralWidget().tabText(1) == 'Listing Workflow'
    assert window.marketdex_workspace_scroll.widget() is content
    for attribute in LISTING_WORKFLOW_WIDGETS:
        assert getattr(window, attribute).parentWidget() is not panel
    window.close()
