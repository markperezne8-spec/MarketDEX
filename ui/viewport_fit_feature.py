from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QTabWidget, QWidget, QVBoxLayout


LISTING_WORKFLOW_WIDGETS = (
    'inventory_listing_workspace',
    'inventory_listing_plan_queue',
    'inventory_listing_execution_readiness',
    'inventory_marketplace_listing_preparation',
    'inventory_marketplace_listing_package_review',
    'inventory_completed_listing_package_queue',
)


def _scroll_page(widget, parent):
    page = QWidget(parent)
    layout = QVBoxLayout(page)
    scroll = QScrollArea(page)
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll.setWidget(widget)
    layout.addWidget(scroll)
    return page, scroll


def install_viewport_fit_feature(window):
    content = window.takeCentralWidget()
    panel_layout = window.inventory_panel.layout()
    listing_content = QWidget()
    listing_layout = QVBoxLayout(listing_content)

    for attribute in LISTING_WORKFLOW_WIDGETS:
        widget = getattr(window, attribute)
        panel_layout.removeWidget(widget)
        listing_layout.addWidget(widget)
    listing_layout.addStretch(1)

    tabs = QTabWidget(window)
    inventory_page, inventory_scroll = _scroll_page(content, tabs)
    listing_page, listing_scroll = _scroll_page(listing_content, tabs)
    tabs.addTab(inventory_page, 'Inventory & Pricing')
    tabs.addTab(listing_page, 'Listing Workflow')
    window.setCentralWidget(tabs)
    window.marketdex_workspace_tabs = tabs
    window.marketdex_workspace_scroll = inventory_scroll
    window.marketdex_listing_workflow_scroll = listing_scroll
