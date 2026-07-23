from PySide6.QtWidgets import QApplication, QGridLayout, QWidget

from ui.data_freshness_feature import install_data_freshness_feature


def _application():
    return QApplication.instance() or QApplication([])


def test_feature_mounts_panel_in_mission_control_grid():
    _application()
    window = QWidget()
    window.dashboard_grid = QGridLayout(window)

    panel = install_data_freshness_feature(window)

    assert window.data_freshness_panel is panel
    assert window.dashboard_grid.indexOf(panel) >= 0
    index = window.dashboard_grid.indexOf(panel)
    row, column, row_span, column_span = window.dashboard_grid.getItemPosition(index)
    assert (row, column, row_span, column_span) == (6, 0, 1, 2)
    assert panel.property('dashboardRole') == 'data-freshness-shell'
