from PySide6.QtWidgets import QWidget,QVBoxLayout,QPushButton
class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout(self)
        for t in ["Mission Control","Collections","Business","Intelligence","System"]:
            l.addWidget(QPushButton(t))
        l.addStretch()
