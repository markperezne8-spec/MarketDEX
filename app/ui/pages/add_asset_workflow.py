from PySide6.QtWidgets import QMessageBox
from app.ui.dialogs.add_asset_dialog import AddAssetDialog

def launch_add_asset(parent):
    dlg=AddAssetDialog(parent)
    if dlg.exec():
        QMessageBox.information(parent,"Saved",
        "Asset dialog completed. Database save will be connected in Alpha 2.4.4.")
