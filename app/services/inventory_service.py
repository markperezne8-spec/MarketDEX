from app.services.asset_service import AssetService

class InventoryService:
    def __init__(self):
        self.assets = AssetService()

    def total_assets(self):
        return len(self.assets.get_assets())

    def all(self):
        return self.assets.get_assets()
