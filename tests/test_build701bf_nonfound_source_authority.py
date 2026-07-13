import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication

from reports.definitions import build_report_catalog
from reports.inventory_age_query import INPUT_NOT_FOUND, InventoryAgeReportQueryResult
from ui.reports_workspace import ReportsWorkspace


def test_build701bf_nonfound_result_shows_inventory_source_authority() -> None:
    app = QApplication.instance() or QApplication([])
    workspace = ReportsWorkspace(build_report_catalog())

    workspace._render_result(
        InventoryAgeReportQueryResult(INPUT_NOT_FOUND, reason='not found'),
        'Inventory Age Patterns',
        'test-position',
    )

    values = {
        workspace.result_table.item(index, 0).text():
        workspace.result_table.item(index, 1).text()
        for index in range(workspace.result_table.rowCount())
    }
    assert values['Source domain'] == 'inventory'
    workspace.close()
