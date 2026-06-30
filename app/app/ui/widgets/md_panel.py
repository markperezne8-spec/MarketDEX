from PySide6.QtWidgets import QFrame,QVBoxLayout,QLabel
class MDPanel(QFrame):
    def __init__(self,title="Panel"):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout=QVBoxLayout(self)
        layout.addWidget(QLabel(title))
