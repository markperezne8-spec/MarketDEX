from uuid import uuid4

from PySide6.QtCore import QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QApplication,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
)

from services.inventory_app_service import LISTING_STATUSES, SHIPPING_PATHS, DRAFT_MARKETPLACES, DRAFT_STATUSES
from services.market_pricing_service import MarketPricingService, PRICE_UPDATED


LISTING_FILTER_STATUSES = ('ALL',) + LISTING_STATUSES
LISTING_MARKETPLACES = ('ALL', 'eBay', 'TCGplayer', 'Other')
DRAFT_FILTER_STATUSES = ('ALL',) + DRAFT_STATUSES



class MarketPriceWorker(QThread):
    result_ready = Signal(object)

    def __init__(self, pricing_service, asset_id):
        super().__init__()
        self.pricing_service = pricing_service
        self.asset_id = asset_id

    def run(self):
        try:
            self.result_ready.emit(self.pricing_service.refresh_price(self.asset_id))
        except Exception as exc:
            self.result_ready.emit({'market_price_worker_error': str(exc)})


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
        self.shipping_path = QComboBox()
        self.shipping_path.addItems(SHIPPING_PATHS)
        self.shipping_path.setCurrentText(detail.get('shipping_path', 'Not Evaluated'))
        self.shipping_notes = QLineEdit(detail.get('shipping_notes', ''))
        form.addRow('Shipping Path', self.shipping_path)
        form.addRow('Shipping Notes', self.shipping_notes)
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



class MarketPriceHistoryDialog(QDialog):
    def __init__(self, rows, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Market Price History')
        form = QFormLayout(self)
        self.table = QTableWidget(len(rows), 6)
        self.table.setHorizontalHeaderLabels(
            ('Observed', 'Price', 'Status', 'Source', 'Match', 'Error')
        )
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        for row_index, row in enumerate(rows):
            status = str(row.get('price_status', '') or '')
            price = row.get('market_price_minor')
            if status == PRICE_UPDATED and price is not None:
                price_text = '{} ${:,.2f}'.format(
                    row.get('currency', 'USD'), int(price) / 100
                )
            else:
                price_text = 'Price unavailable'
            values = (
                row.get('observed_at', '') or '—',
                price_text,
                status.replace('_', ' ').title() or 'Unknown',
                row.get('source_name', '') or '—',
                row.get('match_reference', '') or '—',
                row.get('error_message', '') or '—',
            )
            for column, value in enumerate(values):
                self.table.setItem(row_index, column, QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()
        form.addRow('Observations', self.table)
        if not rows:
            self.empty_state = QLabel('No market price observations recorded yet.')
            form.addRow('', self.empty_state)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.clicked.connect(lambda: self.reject())
        form.addRow('', buttons)


class ListingDraftDialog(QDialog):
    def __init__(self, detail, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Inventory Listing Draft')
        form = QFormLayout(self)
        self.marketplace = QComboBox()
        self.marketplace.addItems(DRAFT_MARKETPLACES)
        self.marketplace.setCurrentText(detail.get('draft_marketplace') or detail.get('marketplace', 'eBay') or 'eBay')
        self.listing_title = QLineEdit(detail.get('draft_listing_title') or detail.get('listing_title', ''))
        self.description_notes = QLineEdit(detail.get('draft_description_notes') or detail.get('listing_notes', ''))
        self.asking_price = QDoubleSpinBox()
        self.asking_price.setRange(0, 1000000)
        self.asking_price.setDecimals(2)
        self.asking_price.setPrefix(chr(36))
        self.asking_price.setValue(int(detail.get('draft_asking_price_minor', detail.get('asking_price_minor', 0))) / 100)
        self.quantity = QDoubleSpinBox()
        self.quantity.setRange(1, max(1, int(detail.get('quantity', 1))))
        self.quantity.setDecimals(0)
        self.quantity.setValue(int(detail.get('draft_quantity') or detail.get('quantity', 1)))
        self.sku = QLineEdit(detail.get('draft_sku') or detail.get('sku', ''))
        self.shipping_method = QComboBox()
        self.shipping_method.addItems(SHIPPING_PATHS)
        self.shipping_method.setCurrentText(detail.get('draft_shipping_method') or detail.get('shipping_path', 'Not Evaluated'))
        self.draft_status = QComboBox()
        self.draft_status.addItems(DRAFT_STATUSES)
        self.draft_status.setCurrentText(detail.get('draft_status') or 'Draft')
        for label, widget in (('Marketplace', self.marketplace), ('Listing Title', self.listing_title), ('Description / Notes', self.description_notes), ('Asking Price', self.asking_price), ('Quantity', self.quantity), ('SKU', self.sku), ('Shipping Method', self.shipping_method), ('Draft Status', self.draft_status)):
            form.addRow(label, widget)
        self.market_price_value = QLabel()
        self.market_price_status = QLabel()
        self.market_price_updated = QLabel()
        self.market_price_source = QLabel()
        self.market_price_source.setWordWrap(True)
        self.refresh_price_button = QPushButton('Refresh Price')
        form.addRow('Market Price', self.market_price_value)
        form.addRow('Price Status', self.market_price_status)
        form.addRow('Updated', self.market_price_updated)
        form.addRow('Source', self.market_price_source)
        form.addRow('', self.refresh_price_button)
        self.market_price_history_button = QPushButton('View Price History')
        form.addRow('', self.market_price_history_button)
        self.set_market_price_detail(detail)
        self.copy_title = QPushButton('Copy Title')
        self.copy_title.clicked.connect(lambda: QApplication.clipboard().setText(self.listing_title.text()))
        self.copy_description = QPushButton('Copy Description')
        self.copy_description.clicked.connect(lambda: QApplication.clipboard().setText(self.description_notes.text()))
        copy_buttons = QHBoxLayout()
        copy_buttons.addWidget(self.copy_title)
        copy_buttons.addWidget(self.copy_description)
        form.addRow(copy_buttons)
        dialog_buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        dialog_buttons.accepted.connect(self.accept)
        dialog_buttons.rejected.connect(self.reject)
        form.addRow(dialog_buttons)


    def set_market_price_detail(self, detail):
        status = detail.get('online_market_price_status', 'PRICE_UNAVAILABLE')
        price_minor = detail.get('online_market_price_minor')
        currency = detail.get('online_market_currency', 'USD')
        if status == PRICE_UPDATED and price_minor is not None:
            self.market_price_value.setText(f'{currency} ${int(price_minor) / 100:,.2f}')
            self.market_price_status.setText('Updated')
        else:
            self.market_price_value.setText('Price unavailable')
            error = detail.get('online_market_error_message', '') or status.replace('_', ' ').title()
            self.market_price_status.setText(f'Price unavailable — {error}')
        self.market_price_updated.setText(detail.get('online_market_updated_at') or 'Never')
        source = detail.get('online_market_source_name') or 'TCGplayer API'
        self.market_price_source.setText(source)
        self.market_price_source.setToolTip(detail.get('online_market_source_url', ''))


def _reconnect(signal, callback):
    try:
        signal.disconnect()
    except (RuntimeError, TypeError):
        pass
    signal.connect(callback)



def _market_price_service(window):
    service = getattr(window, 'market_pricing_service', None)
    if service is None:
        service = MarketPricingService(window.inventory_service)
        window.market_pricing_service = service
    return service


def _online_market_summary(detail):
    status = detail.get('online_market_price_status', 'PRICE_UNAVAILABLE')
    if status == PRICE_UPDATED and detail.get('online_market_price_minor') is not None:
        value = f"{detail.get('online_market_currency', 'USD')} ${int(detail['online_market_price_minor']) / 100:,.2f}"
    else:
        value = 'Price unavailable'
    source = detail.get('online_market_source_name') or 'TCGplayer API'
    updated = detail.get('online_market_updated_at') or 'Never'
    return f"{value} • Status: {status} • Updated: {updated} • Source: {source}"


def _show_market_price_history(window, asset_id, parent=None):
    rows = window.inventory_service.list_market_price_history(asset_id)
    MarketPriceHistoryDialog(rows, parent or window).exec()


def _finish_market_price_refresh(window, asset_id, result, dialog=None):
    if dialog is not None:
        if 'market_price_worker_error' in result:
            dialog.market_price_status.setText(
                f"Price unavailable — {result['market_price_worker_error']}"
            )
        else:
            dialog.set_market_price_detail(result)
        dialog.refresh_price_button.setEnabled(True)
    window.refresh()


def _start_market_price_refresh(window, asset_id, dialog=None, force=True):
    if asset_id is None:
        return
    workers = getattr(window, '_market_price_workers', None)
    if workers is None:
        workers = {}
        window._market_price_workers = workers
    if asset_id in workers:
        return
    if dialog is not None:
        dialog.refresh_price_button.setEnabled(False)
        dialog.market_price_status.setText('Refreshing…')
    worker = MarketPriceWorker(_market_price_service(window), asset_id)
    workers[asset_id] = worker
    worker.result_ready.connect(
        lambda result: _finish_market_price_refresh(window, asset_id, result, dialog)
    )
    worker.finished.connect(lambda: workers.pop(asset_id, None))
    worker.start()


def _schedule_stale_market_price_refresh(window):
    pricing_service = _market_price_service(window)
    if not getattr(pricing_service.provider, 'token', ''):
        return
    rows = window.inventory_service.list_inventory(
        include_details=True,
        listing_status='Ready to List',
    )
    for row in rows:
        if pricing_service.is_stale(row):
            _start_market_price_refresh(window, row['asset_id'], force=False)


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
            shipping_path=dialog.shipping_path.currentText(),
            shipping_notes=dialog.shipping_notes.text(),
            request_id=f'ui-listing-{uuid4().hex}',
        )
        window.refresh()
    except Exception as exc:
        QMessageBox.critical(window, 'Listing Details Blocked', str(exc))



def edit_listing_draft(window):
    asset_id = window.selected_asset_id()
    if asset_id is None:
        return
    dialog = ListingDraftDialog(window.inventory_service.get_asset_detail(asset_id), window)
    if dialog.exec() != QDialog.Accepted:
        return
    try:
        window.inventory_service.update_listing_draft(
            asset_id=asset_id,
            marketplace=dialog.marketplace.currentText(),
            listing_title=dialog.listing_title.text(),
            description_notes=dialog.description_notes.text(),
            asking_price_minor=round(dialog.asking_price.value() * 100),
            quantity=int(dialog.quantity.value()),
            sku=dialog.sku.text(),
            shipping_method=dialog.shipping_method.currentText(),
            draft_status=dialog.draft_status.currentText(),
            request_id=f'ui-draft-{uuid4().hex}',
        )
        window.refresh()
    except Exception as exc:
        QMessageBox.critical(window, 'Listing Draft Blocked', str(exc))



def edit_listing_draft(window):
    asset_id = window.selected_asset_id()
    if asset_id is None:
        return
    dialog = ListingDraftDialog(window.inventory_service.get_asset_detail(asset_id), window)
    dialog.refresh_price_button.clicked.connect(
        lambda: _start_market_price_refresh(window, asset_id, dialog=dialog)
    )
    dialog.market_price_history_button.clicked.connect(
        lambda: _show_market_price_history(window, asset_id, parent=dialog)
    )
    if dialog.exec() != QDialog.Accepted:
        return
    try:
        window.inventory_service.update_listing_draft(
            asset_id=asset_id,
            marketplace=dialog.marketplace.currentText(),
            listing_title=dialog.listing_title.text(),
            description_notes=dialog.description_notes.text(),
            asking_price_minor=round(dialog.asking_price.value() * 100),
            quantity=int(dialog.quantity.value()),
            sku=dialog.sku.text(),
            shipping_method=dialog.shipping_method.currentText(),
            draft_status=dialog.draft_status.currentText(),
            request_id=f'ui-draft-{uuid4().hex}',
        )
        window.refresh()
    except Exception as exc:
        QMessageBox.critical(window, 'Listing Draft Blocked', str(exc))


def export_listing_queue(window):
    destination, _ = QFileDialog.getSaveFileName(
        window, 'Export Listing Queue CSV', 'listing-queue.csv', 'CSV Files (*.csv)'
    )
    if not destination:
        return
    try:
        exported = window.inventory_service.export_listing_queue_csv(destination)
        QMessageBox.information(window, 'Listing Queue Exported', f'CSV saved to {exported}')
    except Exception as exc:
        QMessageBox.critical(window, 'Listing Queue Export Blocked', str(exc))


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
    window.inventory_listing_draft_workspace = False

    filter_bar = QHBoxLayout()
    filter_bar.addWidget(QLabel('Listing Status'))
    window.inventory_listing_status_filter = QComboBox()
    window.inventory_listing_status_filter.addItems(LISTING_FILTER_STATUSES)
    filter_bar.addWidget(window.inventory_listing_status_filter)
    filter_bar.addWidget(QLabel('Marketplace'))
    window.inventory_listing_marketplace_filter = QComboBox()
    window.inventory_listing_marketplace_filter.addItems(LISTING_MARKETPLACES)
    filter_bar.addWidget(window.inventory_listing_marketplace_filter)
    window.inventory_listing_draft_button = QPushButton('Listing Drafts')
    window.inventory_listing_draft_button.setCheckable(True)
    window.inventory_listing_draft_button.clicked.connect(lambda: toggle_listing_drafts(window))
    filter_bar.addWidget(window.inventory_listing_draft_button)
    window.inventory_listing_draft_status_filter = QComboBox()
    window.inventory_listing_draft_status_filter.addItems(('ALL', 'Draft', 'Ready', 'Listed', 'Archived'))
    filter_bar.addWidget(window.inventory_listing_draft_status_filter)
    window.inventory_listing_draft_edit_button = QPushButton('Listing Draft')
    window.inventory_listing_draft_edit_button.setEnabled(False)
    window.inventory_listing_draft_edit_button.clicked.connect(lambda: edit_listing_draft(window))
    filter_bar.addWidget(window.inventory_listing_draft_edit_button)
    window.inventory_market_price_refresh_button = QPushButton('Refresh Price')
    window.inventory_market_price_refresh_button.setEnabled(False)
    window.inventory_market_price_refresh_button.clicked.connect(
        lambda: _start_market_price_refresh(window, window.selected_asset_id())
    )
    filter_bar.addWidget(window.inventory_market_price_refresh_button)
    window.inventory_listing_details_button = QPushButton('Listing Details')
    window.inventory_listing_details_button.setEnabled(False)
    window.inventory_listing_details_button.clicked.connect(lambda: edit_listing_details(window))
    filter_bar.addWidget(window.inventory_listing_details_button)
    window.inventory_listing_queue_button = QPushButton('Listing Queue')
    window.inventory_listing_queue_button.setCheckable(True)
    window.inventory_listing_queue_button.clicked.connect(lambda: toggle_listing_queue(window))
    filter_bar.addWidget(window.inventory_listing_queue_button)
    window.inventory_listing_export_button = QPushButton('Export Queue CSV')
    window.inventory_listing_export_button.clicked.connect(lambda: export_listing_queue(window))
    filter_bar.addWidget(window.inventory_listing_export_button)
    filter_bar.addStretch(1)
    panel_layout = window.inventory_panel.layout()
    panel_layout.insertLayout(panel_layout.indexOf(window.inventory_workspace_controls) + 1, filter_bar)

    def refresh_inventory():
        listing = window.inventory_service.list_archived_inventory if window.inventory_view == 'ARCHIVED' else window.inventory_service.list_inventory
        queue = bool(window.inventory_listing_queue and window.inventory_view == 'ACTIVE')
        drafts = bool(window.inventory_listing_draft_workspace and window.inventory_view == 'ACTIVE')
        if drafts:
            window.inventory_rows = window.inventory_service.list_listing_drafts(
                marketplace=window.inventory_listing_marketplace_filter.currentText(),
                draft_status=window.inventory_listing_draft_status_filter.currentText(),
            )
        else:
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
        label = 'listing drafts' if drafts else ('listing queue' if queue else ('archived' if window.inventory_view == 'ARCHIVED' else 'active'))
        window.inventory_result.setText(f"Showing {len(window.inventory_rows):,} {label} inventory asset(s) • {window.inventory_sort.currentText()} {window.inventory_sort_order.currentText()}")
        window.show_selected()
        QTimer.singleShot(0, lambda: _schedule_stale_market_price_refresh(window))

    def show_selected():
        original_show_selected()
        asset_id = window.selected_asset_id()
        window.inventory_listing_details_button.setEnabled(bool(asset_id and window.inventory_view == 'ACTIVE'))
        window.inventory_listing_draft_edit_button.setEnabled(bool(asset_id and window.inventory_view == 'ACTIVE'))
        window.inventory_market_price_refresh_button.setEnabled(bool(asset_id and window.inventory_view == 'ACTIVE'))
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
            + f"\nSHIPPING: {detail.get('shipping_path', 'Not Evaluated')} • SHIPPING NOTES: {detail.get('shipping_notes', '') or '—'}"
            + f"\nONLINE MARKET: {_online_market_summary(detail)}"
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
        (window.inventory_listing_draft_status_filter.currentTextChanged, refresh_inventory),
    ):
        _reconnect(signal, callback)
    _reconnect(window.inventory_table.itemSelectionChanged, window.show_selected)
    window.refresh_inventory()


def toggle_listing_drafts(window):
    window.inventory_listing_draft_workspace = not window.inventory_listing_draft_workspace
    if window.inventory_listing_draft_workspace:
        window.inventory_listing_queue = False; window.inventory_listing_queue_button.setChecked(False)
        window.inventory_view = 'ACTIVE'; window.view_button.setText('View Archived')
    window.inventory_listing_draft_button.setChecked(window.inventory_listing_draft_workspace)
    window.inventory_listing_draft_button.setText('Show All Inventory' if window.inventory_listing_draft_workspace else 'Listing Drafts')
    window.refresh_inventory()
