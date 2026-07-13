import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from datetime import date

from PySide6.QtWidgets import QApplication

from reports.definitions import build_report_catalog
from reports.inventory_age_provider import (
    INPUT_CONFLICTING,
    INPUT_NOT_FOUND,
    INPUT_UNAVAILABLE,
    INPUT_UNLINKED,
)
from reports.inventory_age_query import InventoryAgeReportQueryResult
from ui.reports_workspace import ReportsWorkspace


def _values(workspace: ReportsWorkspace) -> dict[str, str]:
    return {
        workspace.result_table.item(index, 0).text(): workspace.result_table.item(index, 1).text()
        for index in range(workspace.result_table.rowCount())
    }


def test_build701bo_nonfound_outcomes_preserve_complete_context() -> None:
    app = QApplication.instance() or QApplication([])
    for outcome in (
        INPUT_NOT_FOUND,
        INPUT_UNAVAILABLE,
        INPUT_UNLINKED,
        INPUT_CONFLICTING,
    ):
        workspace = ReportsWorkspace(build_report_catalog())
        workspace._render_result(
            InventoryAgeReportQueryResult(outcome, reason=f'{outcome} evidence'),
            'Inventory Age Patterns',
            'Test_Inventory',
            date(2026, 7, 13),
        )

        values = _values(workspace)
        assert values['Outcome'] == outcome.upper()
        assert values['Reason'] == f'{outcome} evidence'
        assert values['Evidence state'] == 'unavailable'
        assert values['Evidence reason'] == f'{outcome} evidence'
        assert values['Source domain'] == 'inventory'
        assert values['Source date'] == 'unavailable · no Inventory detail evidence'
        assert values['Source field'] == 'purchase_date'
        workspace.close()
