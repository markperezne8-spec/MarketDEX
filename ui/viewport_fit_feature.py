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

PRICING_WIDGETS = (
    'inventory_cost_summary',
    'inventory_sale_readiness',
    'inventory_profit_summary',
    'inventory_price_guidance',
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


def _install_inventory_pricing_handoff(window, tabs):
    panel_layout = window.inventory_panel.layout()
    handoff = QGroupBox('🚀 NEXT: PRICING')
    handoff_layout = QVBoxLayout(handoff)
    guidance = QLabel('Select one inventory asset, then continue to Pricing to review cost, fees, shipping, profit, and target ROI.')
    guidance.setWordWrap(True)
    continue_button = QPushButton('Continue to Pricing →')
    continue_button.setEnabled(False)
    continue_button.clicked.connect(lambda: tabs.setCurrentIndex(1))
    handoff_layout.addWidget(guidance)
    handoff_layout.addWidget(continue_button)
    table_index = panel_layout.indexOf(window.inventory_table)
    insert_at = table_index if table_index >= 0 else panel_layout.count()
    panel_layout.insertWidget(insert_at, handoff)
    original_show = window.show_selected

    def show_selected():
        original_show()
        selected = window.selected_asset_id() is not None
        continue_button.setEnabled(selected)
        window.inventory_continue_to_listing_workflow.setEnabled(selected)
        guidance.setText(
            'Asset selected. Continue to Pricing to review cost, fees, shipping, profit, and target ROI.'
            if selected else
            'Select one inventory asset, then continue to Pricing to review cost, fees, shipping, profit, and target ROI.'
        )
        window.inventory_listing_workflow_guidance.setText(
            'Asset selected. Review pricing, then continue to Listing Workflow.'
            if selected else
            'Select an inventory asset before continuing to Listing Workflow.'
        )

    window.show_selected = show_selected
    try:
        window.inventory_table.itemSelectionChanged.disconnect()
    except RuntimeError:
        pass
    window.inventory_table.itemSelectionChanged.connect(window.show_selected)
    window.inventory_pricing_handoff = handoff
    window.inventory_pricing_guidance = guidance
    window.inventory_continue_to_pricing = continue_button
    show_selected()


def _install_listing_workflow_handoff(window, pricing_layout):
    handoff = QGroupBox('🚀 NEXT: LISTING WORKFLOW')
    handoff_layout = QVBoxLayout(handoff)
    guidance = QLabel('Select an inventory asset before continuing to Listing Workflow.')
    guidance.setWordWrap(True)
    continue_button = QPushButton('Continue to Listing Workflow →')
    continue_button.setEnabled(False)
    handoff_layout.addWidget(guidance)
    handoff_layout.addWidget(continue_button)
    pricing_layout.addWidget(handoff)
    window.inventory_listing_workflow_handoff = handoff
    window.inventory_listing_workflow_guidance = guidance
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
    pricing_content = QWidget()
    pricing_layout = QVBoxLayout(pricing_content)
    pricing_title = QLabel('Pricing')
    pricing_title.setStyleSheet('font-size:30px;font-weight:700')
    pricing_layout.addWidget(pricing_title)
    pricing_layout.addWidget(QLabel('PRICE WITH COST, FEES, SHIPPING, PACKAGING, PROFIT, AND TARGET ROI IN VIEW'))
    _install_listing_workflow_handoff(window, pricing_layout)
    for attribute in PRICING_WIDGETS:
        widget = getattr(window, attribute, None)
        if widget is not None:
            panel_layout.removeWidget(widget)
            pricing_layout.addWidget(widget)
    pricing_layout.addStretch(1)
    _compact_inventory_workspace(window)
    tabs = QTabWidget(window)
    inventory_page, inventory_scroll = _scroll_page(content, tabs)
    pricing_page, pricing_scroll = _scroll_page(pricing_content, tabs)
    listing_page, listing_scroll = _scroll_page(listing_content, tabs)
    tabs.addTab(inventory_page, 'Inventory')
    tabs.addTab(pricing_page, 'Pricing')
    tabs.addTab(listing_page, 'Listing Workflow')
    window.inventory_continue_to_listing_workflow.clicked.connect(lambda: tabs.setCurrentIndex(2))
    _install_inventory_pricing_handoff(window, tabs)
    window.setCentralWidget(tabs)
    window.marketdex_workspace_tabs = tabs
    window.marketdex_workspace_scroll = inventory_scroll
    window.marketdex_pricing_workspace_scroll = pricing_scroll
    window.marketdex_listing_workflow_scroll = listing_scroll
