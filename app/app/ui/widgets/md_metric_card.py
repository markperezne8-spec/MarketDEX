from PySide6.QtWidgets import QFrame,QVBoxLayout,QLabel
class MDMetricCard(QFrame):
    def __init__(self,title,value="--"):
        super().__init__()
        l=QVBoxLayout(self)
        l.addWidget(QLabel(title))
        l.addWidget(QLabel(str(value)))
