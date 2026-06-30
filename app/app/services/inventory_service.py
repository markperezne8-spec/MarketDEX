from app.services.asset_service import AssetService

class InventoryService:
    def __init__(self):
        self.service=AssetService()

    def inventory_count(self):
        return len(self.service.assets())
