from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QAbstractScrollArea, QAbstractSpinBox, QApplication, QComboBox


WHEEL_EDIT_CONTROLS = (QAbstractSpinBox, QComboBox)


def _parent_scroll_area(widget):
    parent = widget.parentWidget()
    while parent is not None:
        if isinstance(parent, QAbstractScrollArea):
            return parent
        parent = parent.parentWidget()
    return None


def _angle_scroll_amount(delta, single_step):
    if delta == 0:
        return 0
    wheel_steps = max(1, round(abs(delta) / 120))
    direction = 1 if delta > 0 else -1
    return direction * wheel_steps * max(1, single_step) * 3


def _scroll_workspace(scroll_area, event):
    pixel_delta = event.pixelDelta()
    angle_delta = event.angleDelta()
    vertical = scroll_area.verticalScrollBar()
    horizontal = scroll_area.horizontalScrollBar()

    if not pixel_delta.isNull():
        vertical_amount = pixel_delta.y()
        horizontal_amount = pixel_delta.x()
    else:
        vertical_amount = _angle_scroll_amount(angle_delta.y(), vertical.singleStep())
        horizontal_amount = _angle_scroll_amount(angle_delta.x(), horizontal.singleStep())

    if vertical_amount:
        vertical.setValue(vertical.value() - vertical_amount)
    if horizontal_amount:
        horizontal.setValue(horizontal.value() - horizontal_amount)


class WheelSafeValueControls(QObject):
    """Prevent page scrolling from silently editing value controls."""

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.Wheel and isinstance(watched, WHEEL_EDIT_CONTROLS):
            scroll_area = _parent_scroll_area(watched)
            if scroll_area is not None:
                _scroll_workspace(scroll_area, event)
            event.accept()
            return True
        return super().eventFilter(watched, event)


def install_wheel_safe_value_controls_feature(window):
    app = QApplication.instance()
    if app is None:
        raise RuntimeError('MarketDEX requires QApplication before installing wheel-safe controls.')
    guard = WheelSafeValueControls(window)
    app.installEventFilter(guard)
    window.marketdex_wheel_safe_value_controls = guard
    return guard
