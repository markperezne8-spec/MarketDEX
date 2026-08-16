import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication, QAbstractItemView

from services.collection_position_service import CollectionPositionService
from ui.collection_position_workspace import CollectionPositionWorkspace


def test_collection_workspace_is_read_only_and_handles_empty_state(tmp_path):
    app = QApplication.instance() or QApplication([])
    workspace = CollectionPositionWorkspace(
        CollectionPositionService(tmp_path / 'marketdex.sqlite3')
    )
    assert workspace.objectName() == 'collectionPositionWorkspace'
    assert workspace.results_table.columnCount() == 9
    assert workspace.results_table.editTriggers() == QAbstractItemView.NoEditTriggers
    assert not workspace.results_table.verticalHeader().isVisible()
    assert workspace.authority_card.objectName() == 'marketdexKpiCard'
    assert workspace.authority_card.value_widget.text() == 'READ-ONLY'
    assert workspace.authority_card.comparison_widget.text() == 'AUTHORITY GATE'
    assert workspace.authority_card.evidence_widget.text() == (
        'Product Registry + Inventory projection · no Collection writes'
    )
    assert workspace.results_table.rowCount() == 0
    assert workspace.status_label.text() == 'No Collection positions are currently linked.'
    workspace.close()
