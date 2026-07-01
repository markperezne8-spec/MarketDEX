from PySide6.QtWidgets import QListWidget

ITEMS=["Mission Control","Inventory","Collection","Business","Research","Settings"]

class NavigationPanel(QListWidget):
    def __init__(self,workspace=None):
        super().__init__()
        self.workspace=workspace
        self.addItems(ITEMS)
        self.setMaximumWidth(220)
        self.currentTextChanged.connect(self._changed)
        self.setCurrentRow(0)

    def _changed(self,text):
        if self.workspace:
            self.workspace.show_page(text)
