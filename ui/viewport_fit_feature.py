from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QLabel, QPushButton, QScrollArea, QSizePolicy, QTabWidget, QWidget, QVBoxLayout


LISTING_WORKFLOW_WIDGETS = (
    'inventory_listing_workspace',
    'inventory_listing_plan_queue',
    'inventory_listing_execution_readiness',
    'inventory_marketplace_listing_preparation',
    'inventory_marketplace_listing_package_review',
    'inventory_completed_listing_package_queue',
    'inventory_listing_execution_history',
    'inventory_sale_completion',
)


def _scroll_page(widget, parent):
    page = QWidget(parent)
    layout = QVBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)
    scroll = QScrollArea(page)
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll.setWidget(widget)
    layout.addWidget(scroll)
    return page, scroll


def _compact_inventory_workspace(window):
    panel = window.inventory_panel
    layout = panel.layout()
    layout.setContentsMargins(12, 10, 12, 10)
    layout.setSpacing(5)
    for value in window.values.values():
        value.setStyleSheet('font-size:18px;font-weight:700')
        box = value.parentWidget()
        if isinstance(box, QGroupBox):
            box.setMinimumHeight(54); box.setMaximumHeight(64); box.layout().setContentsMargins(8, 8, 8, 5)
    for value in window.inventory_summary.values():
        value.setStyleSheet('font-size:16px;font-weight:700')
        box = value.parentWidget()
        if isinstance(box, QGroupBox):
            box.setMinimumHeight(48); box.setMaximumHeight(58); box.layout().setContentsMargins(8, 7, 8, 4)
    window.inventory_table.setMinimumHeight(120)
    window.inventory_table.setMaximumHeight(16777215)
    window.inventory_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


def _install_listing_workflow_handoff(window, tabs):
    panel_layout = window.inventory_panel.layout()
    handoff = QGroupBox('🚀 NEXT: LISTING WORKFLOW')
    handoff_layout = QVBoxLayout(handoff)
    guidance = QLabel('Pricing work is complete here. Continue to Listing Workflow for listing decisions, package review, operator handoff, LISTED outcomes, and confirmed sale completion.')
    guidance.setWordWrap(True)
    continue_button = QPushButton('Continue to Listing Workflow →')
    continue_button.clicked.connect(lambda: tabs.setCurrentIndex(1))
    handoff_layout.addWidget(guidance)
    handoff_layout.addWidget(continue_button)
    panel_layout.insertWidget(panel_layout.indexOf(window.refresh_button), handoff)
    window.inventory_listing_workflow_handoff = handoff
    window.inventory_continue_to_listing_workflow = continue_button


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
    _compact_inventory_workspace(window)
    tabs = QTabWidget(window)
    inventory_page, inventory_scroll = _scroll_page(content, tabs)
    listing_page, listing_scroll = _scroll_page(listing_content, tabs)
    tabs.addTab(inventory_page, 'Inventory & Pricing')
    tabs.addTab(listing_page, 'Listing Workflow')
    _install_listing_workflow_handoff(window, tabs)
    window.setCentralWidget(tabs)
    window.marketdex_workspace_tabs = tabs
    window.marketdex_workspace_scroll = inventory_scroll
    window.marketdex_listing_workflow_scroll = listing_scroll
