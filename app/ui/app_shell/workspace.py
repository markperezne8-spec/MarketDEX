from PySide6.QtWidgets import QStackedWidget
from app.ui.pages.mission_control import MissionControlPage
class Workspace(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.addWidget(MissionControlPage())
