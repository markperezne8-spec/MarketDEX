from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QTabWidget, QWidget, QVBoxLayout


def install_viewport_fit_feature(window):
    content = window.takeCentralWidget()
    tabs = QTabWidget(window)

    workspace_page = QWidget()
    workspace_layout = QVBoxLayout(workspace_page)
    workspace_scroll = QScrollArea(workspace_page)
    workspace_scroll.setWidgetResizable(True)
    workspace_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    workspace_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    workspace_scroll.setWidget(content)
    workspace_layout.addWidget(workspace_scroll)

    tabs.addTab(workspace_page, 'Inventory & Pricing')
    tabs.addTab(QWidget(), 'Listing Workflow')
    window.setCentralWidget(tabs)
    window.marketdex_workspace_tabs = tabs
    window.marketdex_workspace_scroll = workspace_scroll
