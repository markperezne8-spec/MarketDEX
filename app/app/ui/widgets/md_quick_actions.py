from PySide6.QtWidgets import QWidget,QVBoxLayout,QPushButton

class MDQuickActions(QWidget):
    def __init__(self):
        super().__init__()
        layout=QVBoxLayout(self)
        for text in ["Add Asset","Import CSV","Backup Database","Settings"]:
            layout.addWidget(QPushButton(text))
        layout.addStretch()
