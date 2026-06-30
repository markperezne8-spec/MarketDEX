from PySide6.QtWidgets import QLineEdit
class MDSearchBar(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Search inventory...")
