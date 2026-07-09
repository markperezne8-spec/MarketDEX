from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView
from core.listing_package_review_repository import ListingPackageReviewRepository
from core.listing_plan_repository import ListingPlanRepository


def install_inventory_completed_listing_package_queue_feature(window):
    review_repository = ListingPackageReviewRepository(window.inventory_service.database)
    plan_repository = ListingPlanRepository(window.inventory_service.database)
    box = QGroupBox('✅ COMPLETED LISTING PACKAGE QUEUE')
    layout = QVBoxLayout(box)
    status = QLabel('Approved offline packages become operator handoff work here.')
    table = QTableWidget(0, 4)
    table.setHorizontalHeaderLabels(['Asset', 'Marketplace', 'Target Price', 'Handoff'])
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    open_package = QPushButton('Open Approved Package')
    open_package.setEnabled(False)
    layout.addWidget(status)
    layout.addWidget(table)
    layout.addWidget(open_package)
    panel_layout = window.inventory_panel.layout()
    panel_layout.insertWidget(panel_layout.indexOf(window.refresh_button), box)
    window.inventory_completed_listing_package_queue = box
    window.inventory_completed_listing_package_queue_status = status
    window.inventory_completed_listing_package_queue_table = table
    window.inventory_open_approved_listing_package = open_package
    queue_rows = []

    def refresh_queue():
        nonlocal queue_rows
        assets = {row['asset_id']: row for row in window.inventory_service.list_inventory()}
        with window.inventory_service.database.read_connection() as connection:
            listed_asset_ids = {
                row['asset_id'] for row in connection.execute(
                    "SELECT asset_id FROM marketplace_publication_allocations WHERE state='ACTIVE'"
                ).fetchall()
            }
        queue_rows = []
        for review in review_repository.list_completed():
            asset = assets.get(review['asset_id'])
            plan = plan_repository.get(review['asset_id'])
            if asset is not None and plan is not None and review['asset_id'] not in listed_asset_ids:
                queue_rows.append((review, asset, plan))
        table.setRowCount(len(queue_rows))
        for index, (_, asset, plan) in enumerate(queue_rows):
            values = (asset['asset_name'], plan['marketplace'], f"${plan['target_sale_price_minor']/100:,.2f}", 'READY FOR OPERATOR HANDOFF')
            for column, value in enumerate(values):
                table.setItem(index, column, QTableWidgetItem(str(value)))
        table.resizeColumnsToContents()
        status.setText(f"COMPLETED PACKAGE QUEUE: {len(queue_rows):,} approved package(s) ready for operator handoff.")
        open_package.setEnabled(False)

    def open_selected_package():
        selected = table.selectionModel().selectedRows()
        if len(selected) != 1:
            return
        review, asset, _ = queue_rows[selected[0].row()]
        for row_index, row in enumerate(window.inventory_rows):
            if row['asset_id'] == review['asset_id']:
                window.inventory_table.selectRow(row_index)
                window.inventory_table.scrollToItem(window.inventory_table.item(row_index, 0))
                status.setText(f"OPERATOR HANDOFF • Opened approved package for {asset['asset_name']}.")
                return

    table.itemSelectionChanged.connect(lambda: open_package.setEnabled(len(table.selectionModel().selectedRows()) == 1))
    open_package.clicked.connect(open_selected_package)
    window.inventory_approve_listing_package.clicked.connect(refresh_queue)
    window.inventory_return_listing_package.clicked.connect(refresh_queue)
    window.inventory_save_listing_plan.clicked.connect(refresh_queue)
    window.refresh_completed_listing_package_queue = refresh_queue
    refresh_queue()
