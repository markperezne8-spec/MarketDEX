from app.ui.widgets.core.base_widget import BaseWidget
class KPICard(BaseWidget):
    def __init__(self,title="",value="",trend=""):
        self.title=title; self.value=value; self.trend=trend
