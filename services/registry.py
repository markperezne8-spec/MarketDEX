from .business_service import BusinessService
from .marketplace_lifecycle_service import MarketplaceLifecycleService
from .m30_acceptance_service import M30AcceptanceService
class Services:
 def __init__(self,db):
  self.business=BusinessService(db); self.lifecycle=MarketplaceLifecycleService(db); self.m30=M30AcceptanceService(db,self.business,self.lifecycle)
