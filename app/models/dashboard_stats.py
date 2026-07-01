from dataclasses import dataclass

@dataclass
class DashboardStats:
    inventory_count:int=0
    total_investment:float=0.0
    portfolio_value:float=0.0
    warehouse_count:int=0
