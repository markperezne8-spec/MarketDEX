import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from datetime import date

from PySide6.QtWidgets import QApplication

from reports.definitions import build_report_catalog
from reports.inventory_age import derive_inventory_age_row
from reports.inventory_age_query import INPUT_FOUND, INPUT_NOT_FOUND, InventoryAgeReportQueryResult
from ui.reports_workspace import ReportsWorkspace


def _values(workspace: ReportsWorkspace) -> dict[str, str]:
    return {
        workspace.result_table.item(index, 0).text(): workspace.result_table.item(index, 1).text()
        for index in range(workspace.result_table.rowCount())
    }


def test_build701bp_nonfound_exposes_unavailable_age() -> None:
    app = QApplication.instance() or QApplication([])
    workspace = ReportsWorkspace(build_report_catalog())
    workspace._render_result(
        InventoryAgeReportQueryResult(INPUT_NOT_FOUND, reason='no Inventory detail evidence'),
        'Inventory Age Patterns',
        'Test_Inventory',
        date(2026, 7, 14),
    )
    values = _values(workspace)
    assert values['Age (days)'] == 'unavailable'
    assert values['Age reason'] == 'no Inventory detail evidence'
    workspace.close()


def test_build701bp_found_preserves_age_semantics() -> None:
    app = QApplication.instance() or QApplication([])
    workspace = ReportsWorkspace(build_report_catalog())
    row = derive_inventory_age_row(
        inventory_position_id='position-1',
        product_id='product-1',
        product_name='Demo Card',
        current_quantity=1,
        inventory_status='completed',
        as_of_date=date(2026, 7, 14),
        source_start_date=date(2026, 7, 1),
    )
    workspace._render_result(
        InventoryAgeReportQueryResult(INPUT_FOUND, row),
        'Inventory Age Patterns',
    )
    values = _values(workspace)
    assert values['Age (days)'] == '13'
    assert values['Age reason'] == 'source_date_available'
    workspace.close()
