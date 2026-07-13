import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication

from reports.definitions import build_report_catalog
from reports.inventory_age_query import INPUT_NOT_FOUND, InventoryAgeReportQueryResult
from ui.reports_workspace import ReportsWorkspace


def test_build701bb_result_status_preserves_selected_report_context() -> None:
    app = QApplication.instance() or QApplication([])
    workspace = ReportsWorkspace(build_report_catalog())

    workspace._render_result(
        InventoryAgeReportQueryResult(INPUT_NOT_FOUND, reason='not found'),
        'Inventory Age Patterns',
    )

    assert workspace.result_status_label.text() == (
        'Inventory Age Patterns: CATALOG-ONLY · NOT_FOUND · not found'
    )
    assert workspace.result_table.item(0, 0).text() == 'Outcome'
    workspace.close()