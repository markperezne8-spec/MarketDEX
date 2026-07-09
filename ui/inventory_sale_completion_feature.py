from uuid import uuid4

from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QSpinBox, QDoubleSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout

from services.marketplace_lifecycle_service import AuthorityBlocked
from services.operator_sale_completion_service import OperatorSaleCompletionService


def install_inventory_sale_completion_feature(window):
    database = window.inventory_service.database
    completion = OperatorSaleCompletionService(database)
    box = QGroupBox('💰 SALE COMPLETION')
    layout = QVBoxLayout(box)
    status = QLabel('Record a confirmed marketplace sale. This is the authoritative SOLD boundary.')
    status.setWordWrap(True)
    form = QFormLayout()
    sale_reference = QLineEdit(); sale_reference.setPlaceholderText('Marketplace order / sale reference')
    quantity = QSpinBox(); quantity.setMinimum(1); quantity.setMaximum(999999)
    revenue = QDoubleSpinBox(); revenue.setMaximum(9999999); revenue.setPrefix('$'); revenue.setDecimals(2)
    fees = QDoubleSpinBox(); fees.setMaximum(9999999); fees.setPrefix('$'); fees.setDecimals(2)
    shipping = QDoubleSpinBox(); shipping.setMaximum(9999999); shipping.setPrefix('$'); shipping.setDecimals(2)
    packaging = QDoubleSpinBox(); packaging.setMaximum(9999999); packaging.setPrefix('$'); packaging.setDecimals(2)
    for label, widget in [('Sale Reference', sale_reference), ('Quantity Sold', quantity), ('Sale Revenue', revenue), ('Marketplace Fees', fees), ('Shipping Cost', shipping), ('Packaging Cost', packaging)]:
        form.addRow(label, widget)
    record = QPushButton('Confirm Sale and Convert Listing to SOLD')
    history = QTableWidget(0, 5)
    history.setHorizontalHeaderLabels(['Asset', 'Marketplace', 'Sale Reference', 'Revenue', 'Profit'])
    history.setEditTriggers(QTableWidget.NoEditTriggers)
    layout.addWidget(status); layout.addLayout(form); layout.addWidget(record); layout.addWidget(history)
    panel_layout = window.inventory_panel.layout()
    panel_layout.insertWidget(panel_layout.indexOf(window.refresh_button), box)
    window.inventory_sale_completion = box
    window.inventory_sale_completion_status = status
    window.inventory_sale_reference = sale_reference
    window.inventory_confirm_sale = record
    window.inventory_sale_history_table = history

    def selected_allocation():
        asset_id = window.selected_asset_id()
        if asset_id is None:
            return None
        with database.read_connection() as connection:
            return connection.execute(
                "SELECT * FROM marketplace_publication_allocations WHERE asset_id=? AND state='ACTIVE' ORDER BY committed_at DESC LIMIT 1",
                (asset_id,),
            ).fetchone()

    def refresh_sales():
        assets = {row['asset_id']: row for row in window.inventory_service.list_inventory()}
        with database.read_connection() as connection:
            rows = connection.execute(
                "SELECT s.*, a.marketplace FROM sales s LEFT JOIN publication_lifecycle_events p ON p.sale_id=s.sale_id AND p.event_type='SOLD_CONVERSION' LEFT JOIN marketplace_publication_allocations a ON a.allocation_id=p.allocation_id ORDER BY s.created_at DESC"
            ).fetchall()
        history.setRowCount(len(rows))
        for index, sale in enumerate(rows):
            asset = assets.get(sale['asset_id'])
            values = (asset['asset_name'] if asset else sale['asset_id'], sale['marketplace'] or '—', sale['sale_id'], f"${sale['revenue_minor']/100:,.2f}", f"${sale['profit_minor']/100:,.2f}")
            for column, value in enumerate(values): history.setItem(index, column, QTableWidgetItem(str(value)))
        history.resizeColumnsToContents()
        allocation = selected_allocation()
        record.setEnabled(bool(allocation and sale_reference.text().strip() and revenue.value() > 0))
        if allocation:
            remaining = int(allocation['allocated_quantity']) - int(allocation['released_quantity']) - int(allocation['cancelled_quantity']) - int(allocation['consumed_quantity'])
            quantity.setMaximum(max(1, remaining))

    def complete_selected_sale():
        allocation = selected_allocation()
        reference = sale_reference.text().strip()
        if allocation is None or not reference:
            status.setText('SALE BLOCKED • Active recorded listing and sale reference are required.')
            return
        token = uuid4().hex
        try:
            completion.complete_sale(
                sale_request_id=f'OPERATOR-SALE-{token}', conversion_request_id=f'OPERATOR-SOLD-{token}',
                sale_id=f'SALE-OPERATOR-{token}', allocation_id=allocation['allocation_id'],
                sale_quantity=quantity.value(), revenue_minor=round(revenue.value()*100),
                marketplace_fees_minor=round(fees.value()*100), shipping_minor=round(shipping.value()*100),
                packaging_minor=round(packaging.value()*100), evidence_reference=reference, intent='SOLD',
            )
        except (AuthorityBlocked, ValueError) as exc:
            status.setText(f'SALE BLOCKED • {exc}')
            refresh_sales(); return
        status.setText(f"SOLD RECORDED • {allocation['marketplace']} • {reference}")
        sale_reference.clear(); revenue.setValue(0); fees.setValue(0); shipping.setValue(0); packaging.setValue(0)
        window.refresh_inventory(); refresh_sales()
        if hasattr(window, 'refresh_listing_execution_history'): window.refresh_listing_execution_history()

    record.clicked.connect(complete_selected_sale)
    sale_reference.textChanged.connect(refresh_sales)
    revenue.valueChanged.connect(refresh_sales)
    window.inventory_table.itemSelectionChanged.connect(refresh_sales)
    window.refresh_sale_completion = refresh_sales
    refresh_sales()
