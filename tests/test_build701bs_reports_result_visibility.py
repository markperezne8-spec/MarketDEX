import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication

from reports.definitions import build_report_catalog
from ui.reports_workspace import ReportsWorkspace


def test_build701bs_reports_result_surface_prioritizes_result_visibility() -> None:
    app = QApplication.instance() or QApplication([])
    workspace = ReportsWorkspace(build_report_catalog())
    assert workspace.report_table.maximumHeight() == 190
    assert workspace.result_table.minimumHeight() == 360
    workspace.close()
