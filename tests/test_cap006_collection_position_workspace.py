import os
from types import SimpleNamespace

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
    assert workspace.empty_state_panel.objectName() == 'collectionPositionEmptyState'
    assert not workspace.empty_state_panel.isHidden()
    assert workspace.empty_state_title_label.text() == 'No linked Collection positions'
    assert workspace.field_authority_panel.objectName() == (
        'collectionPositionFieldAuthority'
    )
    assert workspace.field_authority_title_label.text() == (
        'Unrecorded Collection fields'
    )
    assert 'does not infer or write' in (
        workspace.field_authority_detail_label.text()
    )

    workspace.search_input.setText('missing')
    workspace.refresh_results()
    assert not workspace.empty_state_panel.isHidden()
    assert workspace.empty_state_title_label.text() == 'No matching Collection positions'

    class StubService:
        def __init__(self):
            self.rows = ()

        def list_positions(self, _query=''):
            return self.rows

    stub = StubService()
    populated_workspace = CollectionPositionWorkspace(stub)
    stub.rows = (
        SimpleNamespace(
            canonical_name='Sample product',
            product_id='PROD-001',
            asset_id='ASSET-001',
            quantity=1,
            storage_location='Shelf A',
            purchase_date='2026-01-01',
            purchase_source='purchase',
            condition_grade=None,
            collector_intent=None,
        ),
    )
    populated_workspace.refresh_results()
    assert populated_workspace.results_table.rowCount() == 1
    assert populated_workspace.results_table.item(0, 7).text() == 'Not recorded'
    assert populated_workspace.results_table.item(0, 8).text() == 'Not recorded'
    assert populated_workspace.empty_state_panel.isHidden()

    stub.rows = ()
    populated_workspace.refresh_results()
    assert not populated_workspace.empty_state_panel.isHidden()
    populated_workspace.close()
    workspace.close()
