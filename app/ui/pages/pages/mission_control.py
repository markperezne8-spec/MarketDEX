from PySide6.QtWidgets import QWidget,QGridLayout,QGroupBox,QVBoxLayout,QLabel,QPushButton
from app.services.dashboard_service import DashboardService

class MissionControlPage(QWidget):
    def __init__(self):
        super().__init__()
        self.service=DashboardService()
        self.labels={}
        grid=QGridLayout(self)

        self._card(grid,0,0,"📦 Inventory","inventory_count")
        self._card(grid,0,1,"💰 Investment","total_investment")
        self._card(grid,1,0,"📈 Portfolio","portfolio_value")
        self._card(grid,1,1,"🏢 Warehouses","warehouse_count")

        actions=QGroupBox("⚡ Quick Actions")
        al=QVBoxLayout(actions)
        for t in ["Add Inventory","Import CSV","Open Purchases","Settings","Refresh Dashboard"]:
            b=QPushButton(t)
            if t=="Refresh Dashboard":
                b.clicked.connect(self.refresh)
            al.addWidget(b)
        grid.addWidget(actions,2,0,1,2)
        self.refresh()

    def _card(self,grid,r,c,title,key):
        box=QGroupBox(title)
        lay=QVBoxLayout(box)
        lbl=QLabel("--")
        lay.addWidget(lbl)
        self.labels[key]=lbl
        grid.addWidget(box,r,c)

    def refresh(self):
        s=self.service.get_stats()
        self.labels["inventory_count"].setText(f"{s.inventory_count} Items")
        self.labels["total_investment"].setText(f"${s.total_investment:,.2f}")
        self.labels["portfolio_value"].setText(f"${s.portfolio_value:,.2f}")
        self.labels["warehouse_count"].setText(str(s.warehouse_count))
