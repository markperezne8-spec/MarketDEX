from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView
from core.listing_plan_repository import ListingPlanRepository


def install_inventory_listing_plan_queue_feature(window):
    repository = ListingPlanRepository(window.inventory_service.database)
    box = QGroupBox('📋 LISTING PLAN QUEUE')
    layout = QVBoxLayout(box)
    status = QLabel('Saved listing plans become operator-ready work here.')
    table = QTableWidget(0, 4)
    table.setHorizontalHeaderLabels(['Asset', 'Marketplace', 'Target Price', 'Target ROI'])
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    open_plan = QPushButton('Open Selected Plan')
    open_plan.setEnabled(False)
    layout.addWidget(status); layout.addWidget(table); layout.addWidget(open_plan)
    panel_layout = window.inventory_panel.layout()
    panel_layout.insertWidget(panel_layout.indexOf(window.refresh_button), box)
    window.inventory_listing_plan_queue = box
    window.inventory_listing_plan_queue_table = table
    window.inventory_listing_plan_queue_status = status
    window.inventory_open_listing_plan = open_plan
    plan_rows = []

    def refresh_queue():
        nonlocal plan_rows
        asset_by_id = {row['asset_id']: row for row in window.inventory_service.list_inventory()}
        plan_rows = [plan for plan in repository.list_all() if plan['asset_id'] in asset_by_id]
        table.setRowCount(len(plan_rows))
        for index, plan in enumerate(plan_rows):
            asset = asset_by_id[plan['asset_id']]
            values = (asset['asset_name'], plan['marketplace'], f"${plan['target_sale_price_minor']/100:,.2f}", f"{plan['target_roi_percent']:.1f}%")
            for column, value in enumerate(values): table.setItem(index, column, QTableWidgetItem(str(value)))
        table.resizeColumnsToContents()
        status.setText(f"LISTING QUEUE: {len(plan_rows):,} saved plan(s) ready for operator review.")
        open_plan.setEnabled(False)

    def open_selected_plan():
        selected = table.selectionModel().selectedRows()
        if len(selected) != 1: return
        plan = plan_rows[selected[0].row()]
        for row_index, row in enumerate(window.inventory_rows):
            if row['asset_id'] == plan['asset_id']:
                window.inventory_table.selectRow(row_index)
                window.inventory_table.scrollToItem(window.inventory_table.item(row_index, 0))
                status.setText(f"LISTING QUEUE: Opened {row['asset_name']}.")
                return

    table.itemSelectionChanged.connect(lambda: open_plan.setEnabled(len(table.selectionModel().selectedRows()) == 1))
    open_plan.clicked.connect(open_selected_plan)
    original_save_click = window.inventory_save_listing_plan.click
    window.refresh_listing_plan_queue = refresh_queue
    window.inventory_save_listing_plan.clicked.connect(refresh_queue)
    original_refresh = window.refresh
    def refresh(): original_refresh(); refresh_queue()
    window.refresh = refresh
    refresh_queue()
