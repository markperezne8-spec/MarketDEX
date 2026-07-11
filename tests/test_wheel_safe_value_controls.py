import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication, QComboBox, QDoubleSpinBox, QScrollArea, QVBoxLayout, QWidget

from ui.wheel_safe_value_controls_feature import WheelSafeValueControls


def _application():
    return QApplication.instance() or QApplication([])


def _wheel_event(delta_y):
    return QWheelEvent(
        QPointF(10, 10),
        QPointF(10, 10),
        QPoint(0, 0),
        QPoint(0, delta_y),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.ScrollUpdate,
        False,
    )


def _scroll_workspace_with_control(control):
    content = QWidget()
    content.setMinimumHeight(1200)
    layout = QVBoxLayout(content)
    layout.addSpacing(500)
    layout.addWidget(control)
    layout.addStretch(1)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(content)
    scroll.resize(320, 220)
    scroll.show()
    _application().processEvents()
    scroll.verticalScrollBar().setValue(250)
    return scroll


def test_mouse_wheel_does_not_change_numeric_value_and_still_scrolls_page():
    app = _application()
    control = QDoubleSpinBox()
    control.setRange(0, 100)
    control.setValue(20.0)
    scroll = _scroll_workspace_with_control(control)
    guard = WheelSafeValueControls()
    app.installEventFilter(guard)
    try:
        before_scroll = scroll.verticalScrollBar().value()
        app.sendEvent(control, _wheel_event(-120))
        assert control.value() == 20.0
        assert scroll.verticalScrollBar().value() > before_scroll
        control.setValue(25.0)
        assert control.value() == 25.0
    finally:
        app.removeEventFilter(guard)
        scroll.close()


def test_mouse_wheel_does_not_change_closed_dropdown_selection():
    app = _application()
    control = QComboBox()
    control.addItems(['EBAY', 'TCGPLAYER', 'CUSTOM'])
    control.setCurrentIndex(1)
    scroll = _scroll_workspace_with_control(control)
    guard = WheelSafeValueControls()
    app.installEventFilter(guard)
    try:
        app.sendEvent(control, _wheel_event(-120))
        assert control.currentText() == 'TCGPLAYER'
        control.setCurrentIndex(2)
        assert control.currentText() == 'CUSTOM'
    finally:
        app.removeEventFilter(guard)
        scroll.close()
