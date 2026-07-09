from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QGroupBox, QLabel, QPushButton, QScrollArea, QSizePolicy, QTabWidget, QWidget, QVBoxLayout


LISTING_WORKFLOW_WIDGETS = (
    'inventory_listing_workspace',
    'inventory_listing_plan_queue',
    'inventory_listing_execution_readiness',
    'inventory_marketplace_listing_preparation',
    'inventory_marketplace_listing_package_review',
    'inventory_completed_listing_package_queue',
)

SALES_WORKFLOW_WIDGETS = (
    'inventory_listing_execution_history',
    'inventory_sale_completion',
)

MISSION_CARDS = (
    ('📦 Inventory Units', 'inventory_units'),
    ('🗂️ Inventory Assets', 'inventory_asset_count'),
    ('💰 Inventory Cost', 'inventory_cost_minor'),
    ('🧾 Completed Sales', 'completed_sales'),
    ('📈 Revenue', 'revenue_minor'),
    ('💵 Profit', 'profit_minor'),
    ('🛡️ Verified Audits', 'verified_audits'),
    ('⚙️ Authority Events', 'authority_events'),
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
        box = value.parentWidget()
        if isinstance(box, QGroupBox):
            box.hide()
    for value in window.inventory_summary.values():
        value.setStyleSheet('font-size:16px;font-weight:700')
        box = value.parentWidget()
        if isinstance(box, QGroupBox):
            box.setMinimumHeight(48); box.setMaximumHeight(58); box.layout().setContentsMargins(8, 7, 8, 4)
    window.inventory_table.setMinimumHeight(120)
    window.inventory_table.setMaximumHeight(16777215)
    window.inventory_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


def _mission_control(window, tabs):
    page = QWidget(tabs)
    layout = QVBoxLayout(page)
    layout.setContentsMargins(24, 20, 24, 20)
    layout.setSpacing(12)
    title = QLabel('MarketDEX OS')
    title.setStyleSheet('font-size:36px;font-weight:700')
    subtitle = QLabel('MISSION CONTROL — YOUR BUSINESS AT A GLANCE')
    subtitle.setStyleSheet('font-size:15px;font-weight:600')
    layout.addWidget(title)
    layout.addWidget(subtitle)
    grid = QGridLayout()
    values = {}
    for index, (label, key) in enumerate(MISSION_CARDS):
        box = QGroupBox(label)
        box_layout = QVBoxLayout(box)
        value = QLabel('--')
        value.setStyleSheet('font-size:24px;font-weight:700')
        box_layout.addWidget(value)
        values[key] = value
        grid.addWidget(box, index // 2, index % 2)
    layout.addLayout(grid)
    guidance = QGroupBox('🚀 NEXT ACTION')
    guidance_layout = QVBoxLayout(guidance)
    guidance_text = QLabel('Add or select inventory to begin. MarketDEX will carry the asset through pricing, listing, and sale completion.')
    guidance_text.setWordWrap(True)
    inventory_button = QPushButton('Open Inventory →')
    inventory_button.clicked.connect(lambda: tabs.setCurrentIndex(1))
    guidance_layout.addWidget(guidance_text)
    guidance_layout.addWidget(inventory_button)
    layout.addWidget(guidance)
    layout.addStretch(1)
    window.marketdex_mission_values = values
    window.marketdex_mission_guidance = guidance_text
    return page


def _pricing_workspace(window, tabs):
    page = QWidget(tabs)
    layout = QVBoxLayout(page)
    layout.setContentsMargins(24, 20, 24, 20)
    layout.setSpacing(12)
    title = QLabel('Pricing')
    title.setStyleSheet('font-size:30px;font-weight:700')
    subtitle = QLabel('PRICE WITH COST, FEES, SHIPPING, PACKAGING, AND TARGET ROI IN VIEW')
    subtitle.setStyleSheet('font-size:15px;font-weight:600')
    layout.addWidget(title)
    layout.addWidget(subtitle)
    guidance = QGroupBox('💰 PRICING WORKSPACE')
    guidance_layout = QVBoxLayout(guidance)
    guidance_text = QLabel('Select an inventory asset first. MarketDEX preserves the current pricing authority and calculations while the operator shell separates each business workspace.')
    guidance_text.setWordWrap(True)
    inventory_button = QPushButton('Select Asset in Inventory →')
    inventory_button.clicked.connect(lambda: tabs.setCurrentIndex(1))
    guidance_layout.addWidget(guidance_text)
    guidance_layout.addWidget(inventory_button)
    layout.addWidget(guidance)
    next_step = QGroupBox('🚀 NEXT: LISTINGS')
    next_layout = QVBoxLayout(next_step)
    next_text = QLabel('When pricing is complete, continue to Listings for listing decisions, package review, and operator handoff.')
    next_text.setWordWrap(True)
    listings_button = QPushButton('Continue to Listings →')
    listings_button.clicked.connect(lambda: tabs.setCurrentIndex(3))
    next_layout.addWidget(next_text)
    next_layout.addWidget(listings_button)
    layout.addWidget(next_step)
    layout.addStretch(1)
    window.marketdex_pricing_guidance = guidance_text
    window.marketdex_pricing_inventory_button = inventory_button
    window.marketdex_pricing_listings_button = listings_button
    return page


def _refresh_mission_control(window):
    snapshot = window.service.snapshot()
    for key in ('inventory_units', 'inventory_asset_count', 'completed_sales', 'verified_audits', 'authority_events'):
        window.marketdex_mission_values[key].setText(f'{snapshot[key]:,}')
    for key in ('inventory_cost_minor', 'revenue_minor', 'profit_minor'):
        window.marketdex_mission_values[key].setText(window._money(snapshot[key]))
    if snapshot['inventory_asset_count']:
        window.marketdex_mission_guidance.setText('Inventory is ready. Open Inventory to select an asset and continue its pricing and listing workflow.')
    else:
        window.marketdex_mission_guidance.setText('Add or import your first inventory asset. MarketDEX will carry it through pricing, listing, and sale completion.')


def _install_listing_workflow_handoff(window, tabs):
    panel_layout = window.inventory_panel.layout()
    handoff = QGroupBox('🚀 NEXT: PRICING')
    handoff_layout = QVBoxLayout(handoff)
    guidance = QLabel('Inventory work is complete here. Continue to Pricing to review sale price, true profit, and ROI before listing.')
    guidance.setWordWrap(True)
    continue_button = QPushButton('Continue to Pricing →')
    continue_button.clicked.connect(lambda: tabs.setCurrentIndex(2))
    handoff_layout.addWidget(guidance)
    handoff_layout.addWidget(continue_button)
    refresh_button = getattr(window, 'refresh_button', None)
    insert_at = panel_layout.indexOf(refresh_button) if refresh_button is not None else panel_layout.count()
    panel_layout.insertWidget(insert_at, handoff)
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
    sales_content = QWidget()
    sales_layout = QVBoxLayout(sales_content)
    for attribute in SALES_WORKFLOW_WIDGETS:
        widget = getattr(window, attribute)
        panel_layout.removeWidget(widget)
        sales_layout.addWidget(widget)
    sales_layout.addStretch(1)
    _compact_inventory_workspace(window)
    tabs = QTabWidget(window)
    mission_page = _mission_control(window, tabs)
    inventory_page, inventory_scroll = _scroll_page(content, tabs)
    pricing_page = _pricing_workspace(window, tabs)
    listing_page, listing_scroll = _scroll_page(listing_content, tabs)
    sales_page, sales_scroll = _scroll_page(sales_content, tabs)
    tabs.addTab(mission_page, 'Mission Control')
    tabs.addTab(inventory_page, 'Inventory')
    tabs.addTab(pricing_page, 'Pricing')
    tabs.addTab(listing_page, 'Listings')
    tabs.addTab(sales_page, 'Sales')
    _install_listing_workflow_handoff(window, tabs)
    original_refresh = window.refresh

    def refresh():
        original_refresh()
        _refresh_mission_control(window)

    window.refresh = refresh
    window.setCentralWidget(tabs)
    window.marketdex_workspace_tabs = tabs
    window.marketdex_workspace_scroll = inventory_scroll
    window.marketdex_listing_workflow_scroll = listing_scroll
    window.marketdex_sales_workflow_scroll = sales_scroll
    _refresh_mission_control(window)
