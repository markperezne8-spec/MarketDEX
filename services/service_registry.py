from core.event_repository import EventRepository
from repositories.asset_repository import AssetRepository
from repositories.inventory_repository import InventoryRepository
from .asset_service import AssetService
from .inventory_service import InventoryService
from .sales_service import SalesService
from .marketplace_lifecycle_service import MarketplaceLifecycleService
from .m30_acceptance_service import M30AcceptanceService
class ServiceRegistry:
 def __init__(self,database):
  events=EventRepository(); assets=AssetRepository(); inventory=InventoryRepository(); self.asset=AssetService(database,events,assets); self.inventory=InventoryService(database,events,assets,inventory); self.sales=SalesService(database,events,assets,inventory); self.lifecycle=MarketplaceLifecycleService(database,events); self.m30=M30AcceptanceService(database,self)
