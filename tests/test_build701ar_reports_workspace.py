import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication, QAbstractItemView, QPushButton

from composition.application_composition import ApplicationComposition
from reports.definitions import build_report_catalog
from ui.reports_workspace import ReportsWorkspace
from ui.shell_workspace_catalog import REPORTS_WORKSPACE_ID


def _table_values(table) -> set[str]:
    values: set[str] = set()
    for row in range(table.rowCount()):
        for column in range(table.columnCount()):
            item = table.item(row, column)
            if item is not None:
                values.add(item.text())
    return values


def test_reports_workspace_is_read_only_catalog_surface() -> None:
    app = QApplication.instance() or QApplication([])
    workspace = ReportsWorkspace(build_report_catalog())

    assert workspace.objectName() == 'reportsWorkspace'
    assert workspace.report_table.columnCount() == 4
    assert workspace.report_table.rowCount() == 2
    assert workspace.report_table.editTriggers() == QAbstractItemView.NoEditTriggers
    assert workspace.report_table.item(0, 0).text() == 'Inventory Age Patterns'
    assert workspace.report_table.item(1, 0).text() == 'Inventory Turnover'
    assert workspace.report_table.item(0, 3).text() == 'APPROVED · READ-ONLY'
    assert workspace.report_table.item(1, 3).text() == 'APPROVED · READ-ONLY'
    assert 'catalog only' in workspace.status_label.text()
    workspace.close()


def test_reports_workspace_has_visible_inventory_turnover_panel() -> None:
    app = QApplication.instance() or QApplication([])
    workspace = ReportsWorkspace(build_report_catalog())

    assert workspace.turnover_panel.objectName() == 'reportsInventoryTurnoverPanel'
    assert workspace.turnover_panel.title() == 'Inventory Turnover'
    assert 'read-only visual preview' in workspace.turnover_status_label.text().lower()
    assert workspace.turnover_table.objectName() == 'reportsInventoryTurnoverTable'
    assert workspace.turnover_table.editTriggers() == QAbstractItemView.NoEditTriggers

    values = _table_values(workspace.turnover_table)
    assert 'inventory-turnover-units-v1' in values
    assert 'Turnover percentage' in values
    assert '50.0%' in values
    assert 'Unavailable state' in values
    assert 'Conflict state' in values
    assert 'none · read-only presentation' in values
    assert workspace.turnover_panel.findChildren(QPushButton) == []
    workspace.close()


def test_inventory_turnover_catalog_selection_is_preview_only() -> None:
    app = QApplication.instance() or QApplication([])
    workspace = ReportsWorkspace(build_report_catalog(), query_report=lambda *_: None)  # type: ignore[arg-type]

    workspace.report_table.selectRow(1)
    workspace.review_selected_report()

    assert 'Inventory Turnover' in workspace.result_status_label.text()
    assert 'visible read-only preview only' in workspace.result_status_label.text()
    workspace.close()


def test_application_composition_mounts_reports_workspace(tmp_path) -> None:
    app = QApplication.instance() or QApplication([])
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    window = composition.build_main_window()

    assert isinstance(window.reports_workspace, ReportsWorkspace)
    assert REPORTS_WORKSPACE_ID in window.workspace_host.workspace_ids

    window.workspace_host.activate(REPORTS_WORKSPACE_ID)

    assert window.workspace_host.currentWidget() is window.reports_workspace
    assert window.workspace_host.currentWidget().turnover_panel.title() == 'Inventory Turnover'
    assert window.workspace_host.workspace_context.text() == 'REPORTS'
    assert window.workspace_host.status_message.text() == 'Reports workspace active'
    window.close()
