import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication
from ui.main_window import AddAssetDialog


def test_add_asset_dialog_exposes_business_detail_fields():
    app = QApplication.instance() or QApplication([])
    dialog = AddAssetDialog()
    assert dialog.purchase_date.placeholderText() == 'YYYY-MM-DD'
    assert hasattr(dialog, 'purchase_source')
    assert hasattr(dialog, 'storage_location')
    assert hasattr(dialog, 'notes')
    dialog.close()
