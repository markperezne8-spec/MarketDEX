from PySide6.QtWidgets import QWidget,QVBoxLayout,QGridLayout,QGroupBox,QLabel
from app.ui.widgets.md_dashboard_card import MDDashboardCard

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        layout=QVBoxLayout(self)

        grid=QGridLayout()
        cards=[
            ("Portfolio Value","$0.00"),
            ("Inventory","0"),
            ("Collection","0"),
            ("ROI","0%")
        ]
        for i,(t,v) in enumerate(cards):
            grid.addWidget(MDDashboardCard(t,v),0,i)
        layout.addLayout(grid)

        activity=QGroupBox("Recent Activity")
        al=QVBoxLayout(activity)
        al.addWidget(QLabel("• MarketDEX started"))
        al.addWidget(QLabel("• Database ready"))
        layout.addWidget(activity)

        pulse=QGroupBox("Market Pulse")
        pl=QVBoxLayout(pulse)
        pl.addWidget(QLabel("Coming Soon"))
        layout.addWidget(pulse)
