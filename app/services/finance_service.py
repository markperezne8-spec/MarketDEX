class FinanceService:
    def roi(self,purchase,current):
        if purchase<=0:
            return 0.0
        return ((current-purchase)/purchase)*100
