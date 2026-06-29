class PortfolioService:
    def portfolio_value(self, assets):
        return sum(getattr(a,"current_value",0)*getattr(a,"quantity",1) for a in assets)
