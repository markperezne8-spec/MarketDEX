from core.event_repository import EventRepository
from repositories.asset_repository import AssetRepository
from repositories.inventory_repository import InventoryRepository
from repositories.reconciliation_repository import ReconciliationRepository
from .asset_service import AssetService
from .inventory_service import InventoryService
from .sales_service import SalesService
from .marketplace_lifecycle_service import MarketplaceLifecycleService
from .inventory_adjustment_service import InventoryAdjustmentService
from .m29_acceptance_service import M29AcceptanceService
from .m30_acceptance_service import M30AcceptanceService
from .reconciliation_service import ReconciliationService
from .m31_acceptance_service import M31AcceptanceService
class ServiceRegistry:
 def __init__(self,database):
  events=EventRepository(); assets=AssetRepository(); inventory=InventoryRepository(); self.asset=AssetService(database,events,assets); self.inventory=InventoryService(database,events,assets,inventory); self.sales=SalesService(database,events,assets,inventory); self.lifecycle=MarketplaceLifecycleService(database,events); self.adjustment=InventoryAdjustmentService(database,events,assets,inventory,self.lifecycle); self.m29=M29AcceptanceService(database,self); self.m30=M30AcceptanceService(database,self); self.reconciliation=ReconciliationService(database,events,self.inventory,ReconciliationRepository(),self.lifecycle); self.m31=M31AcceptanceService(database,self)
