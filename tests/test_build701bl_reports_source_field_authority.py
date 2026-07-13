import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from datetime import date

from PySide6.QtWidgets import QApplication

from reports.definitions import build_report_catalog
from reports.inventory_age_query import INPUT_NOT_FOUND, InventoryAgeReportQueryResult
from ui.reports_workspace import ReportsWorkspace


def test_build701bl_all_outcomes_show_inventory_source_field() -> None:
    app = QApplication.instance() or QApplication([])
    workspace = ReportsWorkspace(build_report_catalog())

    workspace._render_result(
        InventoryAgeReportQueryResult(INPUT_NOT_FOUND, reason='no Inventory detail evidence'),
        'Inventory Age Patterns',
        'Test_Inventory',
        date(2026, 7, 13),
    )

    values = {
        workspace.result_table.item(index, 0).text(): workspace.result_table.item(index, 1).text()
        for index in range(workspace.result_table.rowCount())
    }
    assert values['Source domain'] == 'inventory'
    assert values['Source date'] == 'unavailable · no Inventory detail evidence'
    assert values['Source field'] == 'purchase_date'
    workspace.close()
