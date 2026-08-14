from datetime import date
import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QApplication

from reports.definitions import build_report_catalog
from reports.purchase_source_performance_query import PurchaseSourcePerformanceQueryResponse
from ui.reports_workspace import ReportsWorkspace


def test_reports_workspace_runs_purchase_source_performance_through_injected_query(tmp_path):
    app = QApplication.instance() or QApplication([])
    calls = []

    def query(request):
        calls.append(request)
        return PurchaseSourcePerformanceQueryResponse(
            request=request,
            evidence=(),
            source_domains=('inventory', 'sale_completion'),
            source_coverage=('complete',),
            provenance=('test:reports-workspace',),
        )

    workspace = ReportsWorkspace(
        build_report_catalog(),
        purchase_source_query=query,
    )
    workspace.purchase_source_period_start_input.setDate(QDate(2026, 1, 1))
    workspace.purchase_source_period_end_input.setDate(QDate(2026, 2, 1))
    workspace.purchase_source_as_of_input.setDate(QDate(2026, 2, 1))

    workspace.purchase_source_run_button.click()

    assert len(calls) == 1
    assert calls[0].period_start == date(2026, 1, 1)
    assert calls[0].period_end == date(2026, 2, 1)
    assert calls[0].as_of == date(2026, 2, 1)
    assert 'COVERAGE complete' in workspace.purchase_source_status_label.text()
    workspace.close()


def test_reports_workspace_rejects_invalid_purchase_source_dates_without_querying():
    app = QApplication.instance() or QApplication([])
    calls = []

    def query(request):
        calls.append(request)
        raise AssertionError('invalid request must not reach the query boundary')

    workspace = ReportsWorkspace(
        build_report_catalog(),
        purchase_source_query=query,
    )
    workspace.purchase_source_period_start_input.setDate(QDate(2026, 2, 1))
    workspace.purchase_source_period_end_input.setDate(QDate(2026, 1, 1))
    workspace.purchase_source_as_of_input.setDate(QDate(2026, 1, 1))

    workspace.purchase_source_run_button.click()

    assert calls == []
    assert 'INVALID REQUEST' in workspace.purchase_source_status_label.text()
    workspace.close()
