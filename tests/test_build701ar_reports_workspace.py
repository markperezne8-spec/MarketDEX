import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication, QAbstractItemView, QPushButton

from composition.application_composition import ApplicationComposition
from reports.definitions import build_report_catalog
from ui.reports_workspace import ReportsWorkspace
from ui.shell_workspace_catalog import REPORTS_WORKSPACE_ID


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


def test_reports_workspace_has_visible_inventory_turnover_kpi_dashboard() -> None:
    app = QApplication.instance() or QApplication([])
    workspace = ReportsWorkspace(build_report_catalog())

    assert workspace.turnover_panel.objectName() == 'reportsInventoryTurnoverPanel'
    assert workspace.turnover_panel.title() == 'Inventory Turnover'
    assert workspace.turnover_panel.minimumHeight() >= 250
    assert 'read-only visual preview' in workspace.turnover_status_label.text().lower()

    expected_metrics = {
        'reportsTurnoverPercentage': '50.0%',
        'reportsTurnoverRatio': '0.5×',
        'reportsTurnoverOpeningUnits': '10',
        'reportsTurnoverClosingUnits': '6',
        'reportsTurnoverCompletedSales': '4',
        'reportsTurnoverAverageUnits': '8',
    }
    assert set(workspace.turnover_metric_labels) == set(expected_metrics)
    assert set(workspace.turnover_metric_cards) == set(expected_metrics)
    for object_name, expected_value in expected_metrics.items():
        label = workspace.turnover_metric_labels[object_name]
        card = workspace.turnover_metric_cards[object_name]
        assert label.objectName() == object_name
        assert label.text() == expected_value
        assert label.minimumHeight() >= 26
        assert card.minimumHeight() >= 72
        assert label.isVisibleTo(workspace) is False or not label.isHidden()

    assert workspace.result_table.minimumHeight() <= 180
    assert '2026-01-01' in workspace.turnover_period_label.text()
    assert '2026-02-01' in workspace.turnover_period_label.text()
    assert 'inventory-turnover-units-v1' in workspace.turnover_formula_label.text()
    assert 'EVIDENCE AVAILABLE' in workspace.turnover_evidence_label.text()
    assert 'no mutation authority' in workspace.turnover_evidence_label.text()
    assert 'Unavailable evidence exposes no turnover values' in workspace.turnover_guardrail_label.text()
    assert 'Conflicting evidence blocks numeric output' in workspace.turnover_guardrail_label.text()
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
    assert window.workspace_host.currentWidget().turnover_metric_labels['reportsTurnoverPercentage'].text() == '50.0%'
    assert window.workspace_host.workspace_context.text() == 'REPORTS'
    assert window.workspace_host.status_message.text() == 'Reports workspace active'
    window.close()
