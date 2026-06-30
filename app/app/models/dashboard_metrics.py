from dataclasses import dataclass

@dataclass
class DashboardMetrics:
    inventory_count:int=0
    portfolio_value:float=0.0
    investment_total:float=0.0
    estimated_profit:float=0.0
