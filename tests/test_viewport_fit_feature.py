import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QScrollArea
from ui.viewport_fit_feature import install_viewport_fit_feature


def test_viewport_fit_wraps_workspace_in_resizable_scroll_area():
    app = QApplication.instance() or QApplication([])
    window = QMainWindow()
    content = QWidget()
    window.setCentralWidget(content)
    install_viewport_fit_feature(window)
    assert isinstance(window.centralWidget(), QScrollArea)
    assert window.centralWidget().widget() is content
    assert window.centralWidget().widgetResizable() is True
    window.close()
