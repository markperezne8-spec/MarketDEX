from uuid import uuid4

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
)

from services.inventory_app_service import LISTING_STATUSES


LISTING_FILTER_STATUSES = ('ALL',) + LISTING_STATUSES
LISTING_MARKETPLACES = ('ALL', 'eBay', 'TCGplayer', 'Other')


class ListingDetailsDialog(QDialog):
    def __init__(self, detail, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Inventory Listing Details')
        form = QFormLayout(self)
        blockers = detail.get('readiness_blockers', [])
        readiness_text = detail.get('readiness_state', 'NOT EVALUATED')
        if blockers:
            readiness_text += ' — ' + '; '.join(blockers)
        self.readiness = QLabel(readiness_text)
        self.readiness.setWordWrap(True)
        form.addRow('Readiness', self.readiness)
        self.photos_ready = QComboBox()
        self.photos_ready.addItems(('Not Evaluated', 'Not Ready', 'Ready'))
        self.photos_ready.setCurrentText(detail.get('photos_ready', 'Not Evaluated'))
        self.photo_reference = QLineEdit(detail.get('photo_reference', ''))
        form.addRow('Photos Ready', self.photos_ready)
        form.addRow('Photo Reference', self.photo_reference)
        self.listing_status = QComboBox()
        self.listing_status.addItems(LISTING_STATUSES)
        self.listing_status.setCurrentText(detail.get('listing_status', 'Not Listed'))
        self.marketplace = QComboBox()
        self.marketplace.addItems(('', 'eBay', 'TCGplayer', 'Other'))
        self.marketplace.setCurrentText(detail.get('marketplace', ''))
        self.asking_price = QDoubleSpinBox()
        self.asking_price.setRange(0, 1000000)
        self.asking_price.setDecimals(2)
        self.asking_price.setPrefix('$')
        self.asking_price.setValue(int(detail.get('asking_price_minor', 0)) / 100)
        self.sku = QLineEdit(detail.get('sku', ''))
        self.storage_location = QLineEdit(detail.get('storage_location', ''))
        self.listing_title = QLineEdit(detail.get('listing_title', ''))
        self.listing_notes = QLineEdit(detail.get('listing_notes', ''))
        form.addRow('Listing Status', self.listing_status)
        form.addRow('Marketplace', self.marketplace)
        form.addRow('Asking Price', self.asking_price)
        form.addRow('SKU', self.sku)
        form.addRow('Storage Location', self.storage_location)
        form.addRow('Listing Title', self.listing_title)
        form.addRow('Listing Notes', self.listing_notes)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)


def _reconnect(signal, callback):
    try:
        signal.disconnect()
    except (RuntimeError, TypeError):
        pass
    signal.connect(callback)


def edit_listing_details(window):
    asset_id = window.selected_asset_id()
    if asset_id is None:
        return
    dialog = ListingDetailsDialog(window.inventory_service.get_asset_detail(asset_id), window)
    if dialog.exec() != QDialog.Accepted:
        return
    try:
        window.inventory_service.update_listing_details(
            asset_id=asset_id,
            listing_status=dialog.listing_status.currentText(),
            marketplace=dialog.marketplace.currentText(),
            asking_price_minor=round(dialog.asking_price.value() * 100),
            sku=dialog.sku.text(),
            storage_location=dialog.storage_location.text(),
            listing_title=dialog.listing_title.text(),
            listing_notes=dialog.listing_notes.text(),
            photos_ready=dialog.photos_ready.currentText(),
            photo_reference=dialog.photo_reference.text(),
            request_id=f'ui-listing-{uuid4().hex}',
        )
        window.refresh()
    except Exception as exc:
        QMessageBox.critical(window, 'Listing Details Blocked', str(exc))


def toggle_listing_queue(window):
    window.inventory_listing_queue = not window.inventory_listing_queue
    if window.inventory_listing_queue:
        window.inventory_view = 'ACTIVE'
        window.view_button.setText('View Archived')
    window.inventory_listing_queue_button.setChecked(window.inventory_listing_queue)
    window.inventory_listing_queue_button.setText('Show All Inventory' if window.inventory_listing_queue else 'Listing Queue')
    window.refresh_inventory()


def install_inventory_listing_readiness_feature(window):
    if getattr(window, 'inventory_listing_readiness_installed', False):
        return
    window.inventory_listing_readiness_installed = True
    window.inventory_listing_queue = False

    filter_bar = QHBoxLayout()
    filter_bar.addWidget(QLabel('Listing Status'))
    window.inventory_listing_status_filter = QComboBox()
    window.inventory_listing_status_filter.addItems(LISTING_FILTER_STATUSES)
    filter_bar.addWidget(window.inventory_listing_status_filter)
    filter_bar.addWidget(QLabel('Marketplace'))
    window.inventory_listing_marketplace_filter = QComboBox()
    window.inventory_listing_marketplace_filter.addItems(LISTING_MARKETPLACES)
    filter_bar.addWidget(window.inventory_listing_marketplace_filter)
    window.inventory_listing_details_button = QPushButton('Listing Details')
    window.inventory_listing_details_button.setEnabled(False)
    window.inventory_listing_details_button.clicked.connect(lambda: edit_listing_details(window))
    filter_bar.addWidget(window.inventory_listing_details_button)
    window.inventory_listing_queue_button = QPushButton('Listing Queue')
    window.inventory_listing_queue_button.setCheckable(True)
    window.inventory_listing_queue_button.clicked.connect(lambda: toggle_listing_queue(window))
    filter_bar.addWidget(window.inventory_listing_queue_button)
    filter_bar.addStretch(1)
    panel_layout = window.inventory_panel.layout()
    panel_layout.insertLayout(panel_layout.indexOf(window.inventory_workspace_controls) + 1, filter_bar)

    def refresh_inventory():
        listing = window.inventory_service.list_archived_inventory if window.inventory_view == 'ARCHIVED' else window.inventory_service.list_inventory
        queue = bool(window.inventory_listing_queue and window.inventory_view == 'ACTIVE')
        window.inventory_rows = listing(
            search_text=window.inventory_search.text(),
            asset_type=window.inventory_type_filter.currentText(),
            item_condition=window.inventory_condition_filter.currentText(),
            sort_key=window.inventory_sort.currentText(),
            sort_order=window.inventory_sort_order.currentText(),
            include_details=True,
            listing_status=window.inventory_listing_status_filter.currentText(),
            marketplace=window.inventory_listing_marketplace_filter.currentText(),
            listing_queue=queue,
        )
        window.inventory_table.setRowCount(len(window.inventory_rows))
        summary = window.inventory_service.summarize_inventory(window.inventory_rows)
        window.inventory_summary['asset_count'].setText(f"{summary['asset_count']:,}")
        window.inventory_summary['total_units'].setText(f"{summary['total_units']:,}")
        window.inventory_summary['total_cost_minor'].setText(window._money(summary['total_cost_minor']))
        window.inventory_summary['total_market_value_minor'].setText(window._money(summary.get('total_market_value_minor', 0)))
        window.inventory_summary['estimated_profit_minor'].setText(window._money(summary.get('estimated_profit_minor', -int(summary['total_cost_minor']))))
        for row_index, row in enumerate(window.inventory_rows):
            values = (
                row['asset_name'],
                row['set_name'] or row['product_name'],
                row['asset_type'],
                row['item_condition'],
                row['quantity'],
                window._money(row['total_cost_minor']),
                window._money(row['market_price_minor']),
                row['storage_location'],
                f"{row['notes']} • Readiness: {row.get('readiness_state', 'NOT EVALUATED')} • "
                f"Blockers: {'; '.join(row.get('readiness_blockers', [])) or 'None'}",
            )
            for column, value in enumerate(values):
                window.inventory_table.setItem(row_index, column, QTableWidgetItem(str(value)))
        window.inventory_table.resizeColumnsToContents()
        label = 'listing queue' if queue else ('archived' if window.inventory_view == 'ARCHIVED' else 'active')
        window.inventory_result.setText(f"Showing {len(window.inventory_rows):,} {label} inventory asset(s) • {window.inventory_sort.currentText()} {window.inventory_sort_order.currentText()}")
        window.show_selected()

    def show_selected():
        original_show_selected()
        asset_id = window.selected_asset_id()
        window.inventory_listing_details_button.setEnabled(bool(asset_id and window.inventory_view == 'ACTIVE'))
        if asset_id is None:
            return
        detail = window.inventory_service.get_asset_detail(asset_id)
        blockers = '; '.join(detail.get('readiness_blockers', [])) or 'None'
        window.asset_detail.setText(
            window.asset_detail.text()
            + f"\nLISTING: {detail['listing_status']} • MARKETPLACE: {detail['marketplace'] or '—'} • ASKING: {window._money(detail['asking_price_minor'])} • SKU: {detail['sku'] or '—'}"
            + f"\nTITLE: {detail['listing_title'] or '—'} • LISTING NOTES: {detail['listing_notes'] or '—'}"
            + f"\nREADINESS: {detail.get('readiness_state', 'NOT EVALUATED')} • BLOCKERS: {blockers}"
            + f"\nPHOTOS: {detail.get('photos_ready', 'Not Evaluated')} • PHOTO REFERENCE: {detail.get('photo_reference', '') or '—'}"
        )

    original_show_selected = window.show_selected
    window.refresh_inventory = refresh_inventory
    window.show_selected = show_selected

    for signal, callback in (
        (window.inventory_search.textChanged, refresh_inventory),
        (window.inventory_type_filter.currentTextChanged, refresh_inventory),
        (window.inventory_condition_filter.currentTextChanged, refresh_inventory),
        (window.inventory_sort.currentTextChanged, refresh_inventory),
        (window.inventory_sort_order.currentTextChanged, refresh_inventory),
        (window.inventory_listing_status_filter.currentTextChanged, refresh_inventory),
        (window.inventory_listing_marketplace_filter.currentTextChanged, refresh_inventory),
    ):
        _reconnect(signal, callback)
    _reconnect(window.inventory_table.itemSelectionChanged, window.show_selected)
    window.refresh_inventory()
