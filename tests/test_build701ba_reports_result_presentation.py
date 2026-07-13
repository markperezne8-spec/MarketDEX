import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication

from composition.application_composition import ApplicationComposition
from ui.reports_workspace import ReportsWorkspace


def test_build701ba_reports_result_surface_is_composed(tmp_path) -> None:
    app = QApplication.instance() or QApplication([])
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    window = composition.build_main_window()
    workspace = window.reports_workspace

    assert isinstance(workspace, ReportsWorkspace)
    assert workspace.query_report is not None
    assert workspace.inventory_position_input.objectName() == (
        'reportsInventoryPositionInput'
    )
    assert workspace.as_of_date_input.objectName() == 'reportsAsOfDateInput'
    assert workspace.review_button.objectName() == 'reportsReviewResultButton'
    assert workspace.result_table.columnCount() == 2
    assert 'read-only result' in workspace.result_status_label.text()

    window.close()
