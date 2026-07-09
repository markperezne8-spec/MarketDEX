from uuid import uuid4

from PySide6.QtWidgets import QGroupBox, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout

from core.event_repository import EventRepository
from core.listing_package_review_repository import ListingPackageReviewRepository
from core.listing_plan_repository import ListingPlanRepository
from services.marketplace_lifecycle_service import AuthorityBlocked, MarketplaceLifecycleService


def install_inventory_listing_execution_history_feature(window):
    database = window.inventory_service.database
    reviews = ListingPackageReviewRepository(database)
    plans = ListingPlanRepository(database)
    lifecycle = MarketplaceLifecycleService(database, EventRepository())

    box = QGroupBox('📜 LISTING EXECUTION HISTORY')
    layout = QVBoxLayout(box)
    status = QLabel('Select an approved package, enter the marketplace listing reference, and record the operator outcome.')
    status.setWordWrap(True)
    reference = QLineEdit()
    reference.setPlaceholderText('Marketplace listing reference (order/listing ID or URL reference)')
    record = QPushButton('Record Marketplace Listing as LISTED')
    record.setEnabled(False)
    history = QTableWidget(0, 4)
    history.setHorizontalHeaderLabels(['Asset', 'Marketplace', 'Listing Reference', 'Outcome'])
    history.setEditTriggers(QTableWidget.NoEditTriggers)
    layout.addWidget(status)
    layout.addWidget(reference)
    layout.addWidget(record)
    layout.addWidget(history)

    panel_layout = window.inventory_panel.layout()
    panel_layout.insertWidget(panel_layout.indexOf(window.refresh_button), box)
    window.inventory_listing_execution_history = box
    window.inventory_listing_execution_history_status = status
    window.inventory_listing_reference = reference
    window.inventory_record_listing_outcome = record
    window.inventory_listing_execution_history_table = history

    def selected_context():
        asset_id = window.selected_asset_id()
        if asset_id is None:
            return None, None, None
        row = next((item for item in window.inventory_rows if item['asset_id'] == asset_id), None)
        return row, plans.get(asset_id), reviews.get(asset_id)

    def refresh_history():
        assets = {row['asset_id']: row for row in window.inventory_service.list_inventory()}
        with database.read_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM marketplace_publication_allocations ORDER BY committed_at DESC"
            ).fetchall()
        history.setRowCount(len(rows))
        for index, allocation in enumerate(rows):
            asset = assets.get(allocation['asset_id'])
            values = (
                asset['asset_name'] if asset else allocation['asset_id'],
                allocation['marketplace'],
                allocation['publication_reference'],
                'LISTED • OPERATOR RECORDED',
            )
            for column, value in enumerate(values):
                history.setItem(index, column, QTableWidgetItem(str(value)))
        history.resizeColumnsToContents()

        row, plan, review = selected_context()
        eligible = bool(row and plan and review and review['completed'] == 1 and str(reference.text()).strip())
        if row is not None:
            with database.read_connection() as connection:
                already_listed = connection.execute(
                    'SELECT 1 FROM marketplace_publication_allocations WHERE asset_id=? AND state=?',
                    (row['asset_id'], 'ACTIVE'),
                ).fetchone() is not None
            eligible = eligible and not already_listed
            if already_listed:
                status.setText(f"LISTED • {row['asset_name']} already has an active recorded marketplace listing.")
        record.setEnabled(eligible)

    def record_listed_outcome():
        row, plan, review = selected_context()
        listing_reference = str(reference.text()).strip()
        if row is None or plan is None or review is None or review['completed'] != 1 or not listing_reference:
            status.setText('OUTCOME BLOCKED • Approved completed package and marketplace listing reference are required.')
            refresh_history()
            return
        token = uuid4().hex
        try:
            lifecycle.list_publication(
                request_id=f'OPERATOR-LISTED-{token}',
                allocation_id=f'ALLOC-OPERATOR-{token}',
                asset_id=row['asset_id'],
                marketplace=plan['marketplace'],
                requested_allocation_quantity=int(row['quantity']),
                publication_reference=listing_reference,
                publication_identity=f'OPERATOR-REF-{plan["marketplace"]}-{listing_reference}',
                evidence_type='OPERATOR_RECORDED_MARKETPLACE_OUTCOME',
                evidence_reference=listing_reference,
                evidence_complete=True,
                intent='LISTED',
            )
        except AuthorityBlocked as exc:
            status.setText(f'OUTCOME BLOCKED • {exc}')
            refresh_history()
            return
        status.setText(f"LISTED RECORDED • {row['asset_name']} • {plan['marketplace']} • {listing_reference}")
        reference.clear()
        refresh_history()
        if hasattr(window, 'refresh_completed_listing_package_queue'):
            window.refresh_completed_listing_package_queue()

    reference.textChanged.connect(refresh_history)
    record.clicked.connect(record_listed_outcome)
    window.inventory_table.itemSelectionChanged.connect(refresh_history)
    window.refresh_listing_execution_history = refresh_history
    refresh_history()
