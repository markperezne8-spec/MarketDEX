from core.event_repository import EventRepository
from repositories.asset_repository import AssetRepository
from repositories.inventory_repository import InventoryRepository
from .asset_service import AssetService
from .inventory_service import InventoryService
from .transformation_service import TransformationService
from .sales_service import SalesService
from .return_service import ReturnService
from .exception_service import ExceptionService
from .audit_service import AuditService
from .dashboard_service import DashboardService
class ServiceRegistry:
 def __init__(self,database):
  events=EventRepository(); assets=AssetRepository(); inventory=InventoryRepository()
  self.asset=AssetService(database,events,assets); self.inventory=InventoryService(database,events,assets,inventory)
  self.transformation=TransformationService(database,events,assets,inventory)
  self.sales=SalesService(database,events); self.return_service=ReturnService(database,events); self.exception=ExceptionService(database,events); self.audit=AuditService(database,events); self.dashboard=DashboardService(database,events)
