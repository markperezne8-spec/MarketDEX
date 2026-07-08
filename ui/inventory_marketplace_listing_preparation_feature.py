from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel
from core.listing_plan_repository import ListingPlanRepository
from ui.inventory_listing_execution_readiness_feature import listing_execution_readiness


def marketplace_listing_package(row, plan):
    readiness = listing_execution_readiness(row, plan)
    if not readiness['ready']:
        return {'prepared': False, 'lines': [], 'reason': ', '.join(readiness['missing'])}
    marketplace = str(plan['marketplace']).strip()
    price = int(plan['target_sale_price_minor']) / 100
    title = f"{row['asset_name']} | {row['asset_type']}"
    lines = [
        f"MARKETPLACE: {marketplace}",
        f"TITLE: {title}",
        f"QUANTITY: {int(row['quantity'])}",
        f"TARGET PRICE: ${price:,.2f}",
        f"ASSET ID: {row['asset_id']}",
    ]
    return {'prepared': True, 'lines': lines, 'reason': ''}


def install_inventory_marketplace_listing_preparation_feature(window):
    repository = ListingPlanRepository(window.inventory_service.database)
    box = QGroupBox('📦 MARKETPLACE LISTING PREPARATION')
    layout = QVBoxLayout(box)
    summary = QLabel('Select a READY TO PREPARE asset.')
    summary.setWordWrap(True)
    summary.setStyleSheet('font-size:15px;font-weight:700')
    package = QLabel('LISTING PACKAGE: Waiting for execution readiness.')
    package.setWordWrap(True)
    layout.addWidget(summary)
    layout.addWidget(package)
    panel_layout = window.inventory_panel.layout()
    panel_layout.insertWidget(panel_layout.indexOf(window.refresh_button), box)
    window.inventory_marketplace_listing_preparation = box
    window.inventory_marketplace_listing_preparation_summary = summary
    window.inventory_marketplace_listing_package = package

    def refresh_preparation():
        asset_id = window.selected_asset_id()
        if asset_id is None:
            summary.setText('Select a READY TO PREPARE asset.')
            package.setText('LISTING PACKAGE: Waiting for execution readiness.')
            return
        row = next(row for row in window.inventory_rows if row['asset_id'] == asset_id)
        plan = repository.get(asset_id)
        if plan is None:
            summary.setText(f"PACKAGE BLOCKED • {row['asset_name']} • Save a listing plan first.")
            package.setText('LISTING PACKAGE: Not prepared.')
            return
        result = marketplace_listing_package(row, plan)
        if not result['prepared']:
            summary.setText(f"PACKAGE BLOCKED • {row['asset_name']} • Fix: {result['reason']}")
            package.setText('LISTING PACKAGE: Not prepared.')
            return
        summary.setText(f"LISTING PACKAGE READY • {row['asset_name']} • OFFLINE PREPARATION ONLY")
        package.setText('\n'.join(result['lines']))

    original_show = window.show_selected
    def show_selected():
        original_show()
        refresh_preparation()
    window.show_selected = show_selected
    window.inventory_table.itemSelectionChanged.disconnect()
    window.inventory_table.itemSelectionChanged.connect(window.show_selected)
    window.inventory_save_listing_plan.clicked.connect(refresh_preparation)
    window.refresh_marketplace_listing_preparation = refresh_preparation
    refresh_preparation()
