from app.services.inventory_service import InventoryService

class DashboardService:
    def summary(self):
        inv=InventoryService()
        return {"inventory_count":inv.inventory_count()}
