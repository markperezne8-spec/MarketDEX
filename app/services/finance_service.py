class FinanceService:
    @staticmethod
    def profit(asset):
        return (asset.current_value-asset.purchase_price)*asset.quantity

    @staticmethod
    def roi(asset):
        if asset.purchase_price<=0:
            return 0.0
        return ((asset.current_value-asset.purchase_price)/asset.purchase_price)*100
