from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QWidget,
    QVBoxLayout,
)

from ui.shell_workspace_catalog import (
    INVENTORY_WORKSPACE_ID,
    LISTING_WORKFLOW_WORKSPACE_ID,
    PRICING_WORKSPACE_ID,
    register_core_shell_workspaces,
)
from ui.workspace_host import WorkspaceHost
from ui.workspace_registry import WorkspaceRegistry


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


def _scroll_page(widget: QWidget, parent: QWidget) -> tuple[QWidget, QScrollArea]:
    page = QWidget(parent)
    layout = QVBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)

    scroll = QScrollArea(page)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll.setWidget(widget)
    layout.addWidget(scroll)
    return page, scroll


def _compact_inventory_workspace(window) -> None:
    panel = window.inventory_panel
    layout = panel.layout()
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(7)

    for value in window.values.values():
        value.setStyleSheet('font-size:18px;font-weight:700')
        box = value.parentWidget()
        if isinstance(box, QGroupBox):
            box.setMinimumHeight(54)
            box.setMaximumHeight(64)
            box.layout().setContentsMargins(8, 8, 8, 5)

    for value in window.inventory_summary.values():
        value.setStyleSheet('font-size:16px;font-weight:700')
        box = value.parentWidget()
        if isinstance(box, QGroupBox):
            box.setMinimumHeight(48)
            box.setMaximumHeight(58)
            box.layout().setContentsMargins(8, 7, 8, 4)

    window.inventory_table.setMinimumHeight(120)
    window.inventory_table.setMaximumHeight(16777215)
    window.inventory_table.setSizePolicy(
        QSizePolicy.Expanding,
        QSizePolicy.Expanding,
    )


def _create_handoff_card(
    title: str,
    guidance_text: str,
    button_text: str,
) -> tuple[QGroupBox, QLabel, QPushButton]:
    card = QGroupBox(title)
    card.setObjectName('workspaceHandoffCard')
    layout = QVBoxLayout(card)
    layout.setContentsMargins(14, 14, 14, 12)
    layout.setSpacing(8)

    guidance = QLabel(guidance_text)
    guidance.setObjectName('workspaceHandoffGuidance')
    guidance.setWordWrap(True)

    continue_button = QPushButton(button_text)
    continue_button.setMinimumHeight(34)

    layout.addWidget(guidance)
    layout.addWidget(continue_button)
    return card, guidance, continue_button


def _install_inventory_pricing_handoff(window, host: WorkspaceHost) -> None:
    panel_layout = window.inventory_panel.layout()
    handoff, guidance, continue_button = _create_handoff_card(
        'Next step: Pricing',
        'Select one inventory asset, then review cost, fees, shipping, profit, and target ROI.',
        'Continue to Pricing',
    )
    continue_button.setEnabled(False)
    continue_button.clicked.connect(
        lambda: host.activate(PRICING_WORKSPACE_ID)
    )

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
            if selected
            else 'Select one inventory asset, then review cost, fees, shipping, profit, and target ROI.'
        )
        window.inventory_listing_workflow_guidance.setText(
            'Asset selected. Review pricing, then continue to Listing Workflow.'
            if selected
            else 'Select an inventory asset before continuing to Listing Workflow.'
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


def _install_listing_workflow_handoff(
    window,
    pricing_layout: QVBoxLayout,
    host: WorkspaceHost,
) -> None:
    handoff, guidance, continue_button = _create_handoff_card(
        'Next step: Listing Workflow',
        'Select an inventory asset before continuing to Listing Workflow.',
        'Continue to Listing Workflow',
    )
    continue_button.setEnabled(False)
    continue_button.clicked.connect(
        lambda: host.activate(LISTING_WORKFLOW_WORKSPACE_ID)
    )
    pricing_layout.addWidget(handoff)

    window.inventory_listing_workflow_handoff = handoff
    window.inventory_listing_workflow_guidance = guidance
    window.inventory_continue_to_listing_workflow = continue_button


def _build_listing_workspace(window, panel_layout) -> QWidget:
    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(8)

    for attribute in LISTING_WORKFLOW_WIDGETS:
        widget = getattr(window, attribute)
        panel_layout.removeWidget(widget)
        layout.addWidget(widget)

    layout.addStretch(1)
    return content


def _build_pricing_workspace(
    window,
    panel_layout,
    host: WorkspaceHost,
) -> QWidget:
    content = QWidget()
    content.setObjectName('marketdexPricingWorkspace')
    layout = QVBoxLayout(content)
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(8)

    title = QLabel('Pricing')
    title.setObjectName('marketdexPricingTitle')
    subtitle = QLabel(
        'Price with cost, fees, shipping, packaging, profit, and target ROI in view.'
    )
    subtitle.setObjectName('marketdexPricingSubtitle')
    layout.addWidget(title)
    layout.addWidget(subtitle)

    _install_listing_workflow_handoff(window, layout, host)
    for attribute in PRICING_WIDGETS:
        widget = getattr(window, attribute, None)
        if widget is not None:
            panel_layout.removeWidget(widget)
            layout.addWidget(widget)

    layout.addStretch(1)
    return content


def _publish_shell_handles(
    window,
    registry: WorkspaceRegistry,
    host: WorkspaceHost,
    inventory_scroll: QScrollArea,
    pricing_scroll: QScrollArea,
    listing_scroll: QScrollArea,
) -> None:
    window.workspace_registry = registry
    window.workspace_host = host

    # Compatibility aliases for existing feature and test boundaries.
    window.marketdex_workspace_tabs = host
    window.marketdex_workspace_indexes = host.workspace_indexes
    window.marketdex_workspace_scroll = inventory_scroll
    window.marketdex_pricing_workspace_scroll = pricing_scroll
    window.marketdex_listing_workflow_scroll = listing_scroll


def install_viewport_fit_feature(
    window,
    workspace_registry: WorkspaceRegistry | None = None,
) -> None:
    registry = (
        workspace_registry
        if workspace_registry is not None
        else WorkspaceRegistry()
    )
    content = window.takeCentralWidget()
    if content is None:
        raise RuntimeError('application shell has no central content to compose')

    panel_layout = window.inventory_panel.layout()
    if panel_layout is None:
        raise RuntimeError('inventory panel has no layout')

    host = WorkspaceHost(registry, window)
    listing_content = _build_listing_workspace(window, panel_layout)
    pricing_content = _build_pricing_workspace(window, panel_layout, host)
    _compact_inventory_workspace(window)

    inventory_page, inventory_scroll = _scroll_page(content, host)
    pricing_page, pricing_scroll = _scroll_page(pricing_content, host)
    listing_page, listing_scroll = _scroll_page(listing_content, host)

    register_core_shell_workspaces(
        registry,
        {
            INVENTORY_WORKSPACE_ID: inventory_page,
            PRICING_WORKSPACE_ID: pricing_page,
            LISTING_WORKFLOW_WORKSPACE_ID: listing_page,
        },
    )
    host.mount_registered_workspaces()

    window.setCentralWidget(host)
    _publish_shell_handles(
        window,
        registry,
        host,
        inventory_scroll,
        pricing_scroll,
        listing_scroll,
    )
    _install_inventory_pricing_handoff(window, host)
