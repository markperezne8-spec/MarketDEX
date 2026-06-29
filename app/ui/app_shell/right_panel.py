from PySide6.QtWidgets import QWidget,QVBoxLayout,QGroupBox,QLabel
class RightPanel(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout(self)
        for title in ["Quick Actions","Notifications","Tasks"]:
            g=QGroupBox(title)
            gl=QVBoxLayout(g)
            gl.addWidget(QLabel("Coming Soon"))
            l.addWidget(g)
        l.addStretch()
