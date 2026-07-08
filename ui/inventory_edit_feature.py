from uuid import uuid4
from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QPushButton, QMessageBox
from services.inventory_edit_details_service import edit_inventory_details


class EditAssetDetailsDialog(QDialog):
    def __init__(self, detail, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Edit Inventory Details')
        form = QFormLayout(self)
        self.name = QLineEdit(detail['asset_name'])
        self.asset_type = QComboBox()
        self.asset_type.addItems(['SINGLE', 'SEALED', 'SLAB', 'ACCESSORY'])
        self.asset_type.setCurrentText(detail['asset_type'])
        self.purchase_date = QLineEdit(detail['purchase_date'])
        self.purchase_date.setPlaceholderText('YYYY-MM-DD')
        self.purchase_source = QLineEdit(detail['purchase_source'])
        self.storage_location = QLineEdit(detail['storage_location'])
        self.notes = QLineEdit(detail['notes'])
        form.addRow('Asset Name', self.name)
        form.addRow('Asset Type', self.asset_type)
        form.addRow('Purchase Date', self.purchase_date)
        form.addRow('Purchase Source', self.purchase_source)
        form.addRow('Storage Location', self.storage_location)
        form.addRow('Notes', self.notes)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)


def install_inventory_edit_feature(window):
    button = QPushButton('Edit Details', window)
    button.setObjectName('edit_details_button')
    button.setMinimumWidth(max(button.sizeHint().width(), 96))
    button.setEnabled(False)
    window.edit_details_button = button

    header = window.inventory_header
    insert_at = header.indexOf(window.adjust_button)
    header.insertWidget(insert_at, button)

    panel = window.inventory_panel
    panel.setMaximumWidth(max(panel.maximumWidth(), 1100))

    original_show_selected = window.show_selected

    def show_selected():
        original_show_selected()
        button.setEnabled(window.inventory_view == 'ACTIVE' and window.selected_asset_id() is not None)

    def edit_selected():
        asset_id = window.selected_asset_id()
        if asset_id is None:
            return
        detail = window.inventory_service.get_asset_detail(asset_id)
        dialog = EditAssetDetailsDialog(detail, window)
        if dialog.exec() != QDialog.Accepted:
            return
        try:
            identity_changed = dialog.name.text().strip() != detail['asset_name'] or dialog.asset_type.currentText() != detail['asset_type']
            business_values = {
                'purchase_date': dialog.purchase_date.text(),
                'purchase_source': dialog.purchase_source.text(),
                'storage_location': dialog.storage_location.text(),
                'notes': dialog.notes.text(),
            }
            business_changed = any(str(business_values[key] or '').strip() != detail[key] for key in business_values)
            if identity_changed:
                edit_inventory_details(window.inventory_service, asset_id=asset_id, asset_name=dialog.name.text(), asset_type=dialog.asset_type.currentText(), request_id=f'ui-edit-details-{uuid4().hex}')
            if business_changed:
                window.inventory_service.update_business_details(asset_id=asset_id, request_id=f'ui-business-details-{uuid4().hex}', **business_values)
            if not identity_changed and not business_changed:
                raise ValueError('Enter an inventory detail change')
            window.refresh()
            QMessageBox.information(window, 'Inventory Details Updated', 'Inventory details updated through authoritative events.')
        except Exception as exc:
            QMessageBox.critical(window, 'Edit Details Blocked', str(exc))

    window.show_selected = show_selected
    window.inventory_table.itemSelectionChanged.disconnect()
    window.inventory_table.itemSelectionChanged.connect(window.show_selected)
    button.clicked.connect(edit_selected)
    window.show_selected()
