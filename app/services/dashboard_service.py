from app.models.dashboard_stats import DashboardStats
from app.repositories.inventory_repository import InventoryRepository

class DashboardService:
    def __init__(self):
        self.repo=InventoryRepository()

    def get_stats(self):
        stats=DashboardStats()
        stats.inventory_count=self.repo.count()
        stats.total_investment=self.repo.total_investment()
        stats.portfolio_value=stats.total_investment
        stats.warehouse_count=1
        return stats
