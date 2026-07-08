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
        form.addRow('Asset Name', self.name)
        form.addRow('Asset Type', self.asset_type)
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

    # The original Mission Control panel width predates Archive, Restore, and
    # Edit Details. Preserve every control's readable minimum width instead of
    # allowing Qt to squeeze the new button to zero pixels.
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
            edit_inventory_details(
                window.inventory_service,
                asset_id=asset_id,
                asset_name=dialog.name.text(),
                asset_type=dialog.asset_type.currentText(),
                request_id=f'ui-edit-details-{uuid4().hex}',
            )
            window.refresh()
            QMessageBox.information(window, 'Inventory Details Updated', 'Asset name and type updated through an authoritative event.')
        except Exception as exc:
            QMessageBox.critical(window, 'Edit Details Blocked', str(exc))

    window.show_selected = show_selected
    window.inventory_table.itemSelectionChanged.disconnect()
    window.inventory_table.itemSelectionChanged.connect(window.show_selected)
    button.clicked.connect(edit_selected)
    window.show_selected()
