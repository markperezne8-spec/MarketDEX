from PySide6.QtWidgets import QWidget,QVBoxLayout,QGridLayout
from app.ui.widgets.md_metric_card import MDMetricCard
from app.ui.widgets.md_panel import MDPanel

class MissionControlPage(QWidget):
    def __init__(self):
        super().__init__()
        layout=QVBoxLayout(self)

        grid=QGridLayout()
        grid.addWidget(MDMetricCard("Portfolio","$0.00"),0,0)
        grid.addWidget(MDMetricCard("Inventory","0"),0,1)
        grid.addWidget(MDMetricCard("Collection","0"),0,2)
        grid.addWidget(MDMetricCard("ROI","0%"),0,3)
        layout.addLayout(grid)

        layout.addWidget(MDPanel("Recent Activity"))
        layout.addWidget(MDPanel("Market Overview"))
