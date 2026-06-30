from PySide6.QtWidgets import QMessageBox
from app.models.asset import Asset
from app.services.asset_service import AssetService

service=AssetService()

def save_asset_from_dialog(dialog,parent=None):
    asset=Asset(
        name=dialog.name.text(),
        category=dialog.category.text(),
        set_name=dialog.set_name.text(),
        card_number=dialog.card_number.text(),
        quantity=dialog.qty.value(),
        purchase_price=dialog.cost.value(),
        current_value=dialog.value.value(),
    )
    service.create_asset(asset)
    QMessageBox.information(parent,"MarketDEX","Asset saved successfully.")
