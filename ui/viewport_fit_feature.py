from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea


def install_viewport_fit_feature(window):
    content = window.takeCentralWidget()
    scroll = QScrollArea(window)
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll.setWidget(content)
    window.setCentralWidget(scroll)
    window.marketdex_workspace_scroll = scroll
