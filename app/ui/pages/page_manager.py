from PySide6.QtWidgets import QStackedWidget,QLabel
from PySide6.QtCore import Qt
from app.ui.pages.mission_control import MissionControlPage

class PageManager(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.pages={}
        self.pages["Mission Control"]=self.addWidget(MissionControlPage())
        for name in ["Inventory","Collection","Business","Research","Settings"]:
            lbl=QLabel(name)
            lbl.setAlignment(Qt.AlignCenter)
            self.pages[name]=self.addWidget(lbl)

    def show_page(self,name):
        if name in self.pages:
            self.setCurrentIndex(self.pages[name])
