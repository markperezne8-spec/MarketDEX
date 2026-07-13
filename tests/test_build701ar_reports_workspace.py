import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication, QAbstractItemView

from composition.application_composition import ApplicationComposition
from reports.definitions import build_report_catalog
from ui.reports_workspace import ReportsWorkspace
from ui.shell_workspace_catalog import REPORTS_WORKSPACE_ID


def test_reports_workspace_is_read_only_catalog_surface() -> None:
    app = QApplication.instance() or QApplication([])
    workspace = ReportsWorkspace(build_report_catalog())

    assert workspace.objectName() == 'reportsWorkspace'
    assert workspace.report_table.columnCount() == 4
    assert workspace.report_table.rowCount() == 1
    assert workspace.report_table.editTriggers() == QAbstractItemView.NoEditTriggers
    assert workspace.report_table.item(0, 0).text() == 'Inventory Age Patterns'
    assert workspace.report_table.item(0, 3).text() == 'APPROVED · READ-ONLY'
    assert 'catalog only' in workspace.status_label.text()
    workspace.close()


def test_application_composition_mounts_reports_workspace(tmp_path) -> None:
    app = QApplication.instance() or QApplication([])
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    window = composition.build_main_window()

    assert isinstance(window.reports_workspace, ReportsWorkspace)
    assert REPORTS_WORKSPACE_ID in window.workspace_host.workspace_ids

    window.workspace_host.activate(REPORTS_WORKSPACE_ID)

    assert window.workspace_host.currentWidget() is window.reports_workspace
    assert window.workspace_host.workspace_context.text() == 'REPORTS'
    assert window.workspace_host.status_message.text() == 'Reports workspace active'
    window.close()
