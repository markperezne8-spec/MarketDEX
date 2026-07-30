from PySide6.QtWidgets import QWidget,QGridLayout,QGroupBox,QVBoxLayout,QLabel,QPushButton

class MissionControlPage(QWidget):
    def __init__(self):
        super().__init__()
        grid=QGridLayout(self)
        cards=[
            ("📦 Inventory","0 Items"),
            ("💰 Investment","$0.00"),
            ("📈 Portfolio","$0.00"),
            ("🏢 Warehouses","0")
        ]
        for i,(title,value) in enumerate(cards):
            box=QGroupBox(title)
            lay=QVBoxLayout(box)
            lay.addWidget(QLabel(value))
            grid.addWidget(box,i//2,i%2)
        actions=QGroupBox("⚡ Quick Actions")
        alay=QVBoxLayout(actions)
        for text in ["Add Inventory","Import CSV","Open Purchases","Settings"]:
            alay.addWidget(QPushButton(text))
        grid.addWidget(actions,2,0,1,2)
