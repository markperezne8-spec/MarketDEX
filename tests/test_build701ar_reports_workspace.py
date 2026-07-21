import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication, QAbstractItemView, QPushButton

from composition.application_composition import ApplicationComposition
from reports.definitions import build_report_catalog
from reports.inventory_turnover_presentation import (
    InventoryTurnoverPresentation,
    present_inventory_turnover,
)
from reports.inventory_turnover_preview import build_inventory_turnover_preview_result
from ui.reports_workspace import ReportsWorkspace
from ui.shell_workspace_catalog import REPORTS_WORKSPACE_ID


def _turnover_presentation(**overrides: str) -> InventoryTurnoverPresentation:
    values = {
        'outcome': 'valid',
        'status': 'VALID',
        'reason': 'Bound presentation fixture',
        'period': '2026-03-01 → 2026-04-01',
        'formula': 'inventory-turnover-units-v1',
        'evidence': 'available · closed_period',
        'opening_units': '12',
        'closing_units': '8',
        'average_units': '10',
        'completed_sale_units': '5',
        'turnover_ratio': '0.5×',
        'turnover_percentage': '50.0%',
    }
    values.update(overrides)
    return InventoryTurnoverPresentation(**values)


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


def test_reports_workspace_binds_inventory_turnover_presentation() -> None:
    app = QApplication.instance() or QApplication([])
    presentation = _turnover_presentation()
    workspace = ReportsWorkspace(
        build_report_catalog(),
        turnover_presentation=presentation,
    )

    assert workspace.turnover_presentation is presentation
    assert workspace.turnover_panel.objectName() == 'reportsInventoryTurnoverPanel'
    assert workspace.turnover_panel.title() == 'Inventory Turnover'
    assert workspace.turnover_panel.minimumHeight() >= 250
    assert 'bound presentation fixture' in workspace.turnover_status_label.text().lower()

    expected_metrics = {
        'reportsTurnoverPercentage': '50.0%',
        'reportsTurnoverRatio': '0.5×',
        'reportsTurnoverOpeningUnits': '12',
        'reportsTurnoverClosingUnits': '8',
        'reportsTurnoverCompletedSales': '5',
        'reportsTurnoverAverageUnits': '10',
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
    assert presentation.period in workspace.turnover_period_label.text()
    assert presentation.status in workspace.turnover_period_label.text()
    assert presentation.formula in workspace.turnover_formula_label.text()
    assert presentation.evidence in workspace.turnover_evidence_label.text()
    assert 'no mutation authority' in workspace.turnover_evidence_label.text()
    assert 'Unavailable evidence exposes no turnover values' in workspace.turnover_guardrail_label.text()
    assert 'Conflicting evidence blocks numeric output' in workspace.turnover_guardrail_label.text()
    assert workspace.turnover_panel.findChildren(QPushButton) == []
    workspace.close()


def test_reports_workspace_preserves_unavailable_turnover_values() -> None:
    app = QApplication.instance() or QApplication([])
    presentation = _turnover_presentation(
        outcome='unavailable',
        status='UNAVAILABLE',
        reason='Source coverage unavailable',
        evidence='unavailable',
        opening_units='Unavailable',
        closing_units='Unavailable',
        average_units='Unavailable',
        completed_sale_units='Unavailable',
        turnover_ratio='Unavailable',
        turnover_percentage='Unavailable',
    )
    workspace = ReportsWorkspace(
        build_report_catalog(),
        turnover_presentation=presentation,
    )

    assert 'source coverage unavailable' in workspace.turnover_status_label.text().lower()
    assert all(
        label.text() == 'Unavailable'
        for label in workspace.turnover_metric_labels.values()
    )
    workspace.close()


def test_inventory_turnover_catalog_selection_is_preview_only() -> None:
    app = QApplication.instance() or QApplication([])
    workspace = ReportsWorkspace(build_report_catalog(), query_report=lambda *_: None)  # type: ignore[arg-type]

    workspace.report_table.selectRow(1)
    workspace.review_selected_report()

    assert 'Inventory Turnover' in workspace.result_status_label.text()
    assert 'visible read-only preview only' in workspace.result_status_label.text()
    workspace.close()


def test_inventory_turnover_preview_factory_is_deterministic() -> None:
    first = build_inventory_turnover_preview_result()
    second = build_inventory_turnover_preview_result()

    assert first == second
    assert first is not second
    assert first.provenance == ('reports:deterministic-preview',)
    assert first.turnover_percentage == 50
    assert present_inventory_turnover(first).turnover_percentage == '50%'


def test_application_composition_mounts_reports_workspace(tmp_path) -> None:
    app = QApplication.instance() or QApplication([])
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    assert composition.inventory_turnover_preview_result == (
        build_inventory_turnover_preview_result()
    )
    assert composition.inventory_turnover_presentation == present_inventory_turnover(
        composition.inventory_turnover_preview_result
    )
    assert composition.inventory_turnover_preview_result.provenance == (
        'reports:deterministic-preview',
    )
    assert composition.inventory_turnover_preview_result.turnover_percentage == 50

    window = composition.build_main_window()

    assert isinstance(window.reports_workspace, ReportsWorkspace)
    assert REPORTS_WORKSPACE_ID in window.workspace_host.workspace_ids

    window.workspace_host.activate(REPORTS_WORKSPACE_ID)

    reports_workspace = window.workspace_host.currentWidget()
    assert reports_workspace is window.reports_workspace
    assert reports_workspace.turnover_panel.title() == 'Inventory Turnover'
    assert reports_workspace.turnover_presentation is composition.inventory_turnover_presentation
    assert (
        reports_workspace.turnover_metric_labels['reportsTurnoverPercentage'].text()
        == composition.inventory_turnover_presentation.turnover_percentage
    )
    assert window.workspace_host.workspace_context.text() == 'REPORTS'
    assert window.workspace_host.status_message.text() == 'Reports workspace active'
    window.close()
