from PySide6.QtWidgets import QFrame,QVBoxLayout,QLabel

class MDDashboardCard(QFrame):
    def __init__(self,title,value="--"):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout=QVBoxLayout(self)
        layout.addWidget(QLabel(title))
        value_lbl=QLabel(str(value))
        value_lbl.setStyleSheet("font-size:20px;font-weight:bold;")
        layout.addWidget(value_lbl)
