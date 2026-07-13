import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from datetime import date

from PySide6.QtWidgets import QApplication

from reports.definitions import build_report_catalog
from reports.inventory_age_query import INPUT_NOT_FOUND, InventoryAgeReportQueryResult
from ui.reports_workspace import ReportsWorkspace


def test_build701bd_nonfound_result_preserves_query_context() -> None:
    app = QApplication.instance() or QApplication([])
    workspace = ReportsWorkspace(build_report_catalog())

    workspace._render_result(
        InventoryAgeReportQueryResult(INPUT_NOT_FOUND, reason='not found'),
        'Inventory Age Patterns',
        'test-position',
        date(2026, 7, 13),
    )

    assert workspace.result_table.item(2, 0).text() == 'Inventory position'
    assert workspace.result_table.item(2, 1).text() == 'test-position'
    assert workspace.result_table.item(3, 0).text() == 'As-of date'
    assert workspace.result_table.item(3, 1).text() == '2026-07-13'
    workspace.close()
