from PySide6.QtWidgets import QStatusBar
def build_status_bar(parent):
    bar=QStatusBar(parent)
    bar.showMessage("Ready | Database: Pending | Theme: Dark | Build 001")
    return bar
