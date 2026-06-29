from app.services.inventory_service import InventoryService

class DashboardService:
    def __init__(self):
        self.inventory = InventoryService()

    def dashboard_data(self):
        return {
            "inventory_count": self.inventory.total_assets()
        }
