import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from datetime import date

from PySide6.QtWidgets import QApplication

from reports.definitions import build_report_catalog
from reports.inventory_age import derive_inventory_age_row
from reports.inventory_age_query import INPUT_FOUND, InventoryAgeReportQueryResult
from ui.reports_workspace import ReportsWorkspace


def test_build701be_found_result_shows_source_authority() -> None:
    app = QApplication.instance() or QApplication([])
    workspace = ReportsWorkspace(build_report_catalog())
    row = derive_inventory_age_row(
        inventory_position_id='position-1',
        product_id='product-1',
        product_name='Demo Card',
        current_quantity=1,
        inventory_status='completed',
        as_of_date=date(2026, 7, 13),
        source_start_date=date(2026, 7, 1),
    )

    workspace._render_result(
        InventoryAgeReportQueryResult(INPUT_FOUND, row),
        'Inventory Age Patterns',
    )

    values = [
        workspace.result_table.item(index, 0).text()
        for index in range(workspace.result_table.rowCount())
    ]
    assert 'Source domain' in values
    workspace.close()
