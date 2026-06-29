from PySide6.QtWidgets import QWidget,QHBoxLayout,QLabel,QLineEdit,QPushButton
class Header(QWidget):
    """Top application header."""
    def __init__(self):
        super().__init__()
        l=QHBoxLayout(self)
        l.addWidget(QLabel("MarketDEX"))
        l.addWidget(QLineEdit(placeholderText="Search..."))
        l.addWidget(QPushButton("Theme"))
        l.addWidget(QPushButton("Settings"))
