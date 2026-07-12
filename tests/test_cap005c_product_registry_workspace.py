from PySide6.QtWidgets import QApplication, QAbstractItemView

from services.product_registry_lookup_service import ProductRegistryLookupService
from services.product_registry_service import ProductRegistryService
from ui.product_registry_workspace import ProductRegistryWorkspace


def _app():
    return QApplication.instance() or QApplication([])


def _workspace(tmp_path):
    _app()
    database_path = tmp_path / 'marketdex.db'
    registry = ProductRegistryService(database_path)
    product_id = registry.register(
        'SINGLE',
        'Charizard ex',
        'Obsidian Flames',
        '125/197',
        'Double Rare',
        'CAP005C-WORKSPACE-PRODUCT-001',
    )
    registry.add_alias(product_id, 'Charizard EX 125/197', 'CAP005C-WORKSPACE-ALIAS-001')
    return ProductRegistryWorkspace(ProductRegistryLookupService(database_path)), product_id


def test_workspace_shell_exposes_read_only_search_controls(tmp_path):
    workspace, _ = _workspace(tmp_path)

    assert workspace.objectName() == 'productRegistryWorkspace'
    assert workspace.search_input.objectName() == 'productRegistrySearchInput'
    assert workspace.product_type_filter.objectName() == 'productRegistryTypeFilter'
    assert workspace.search_button.text() == 'Search'
    assert workspace.results_table.columnCount() == 8
    assert workspace.results_table.editTriggers() == QAbstractItemView.NoEditTriggers


def test_workspace_search_renders_stable_product_record(tmp_path):
    workspace, product_id = _workspace(tmp_path)
    workspace.search_input.setText('Charizard EX 125/197')

    workspace.refresh_results()

    assert workspace.results_table.rowCount() == 1
    assert workspace.results_table.item(0, 0).text() == product_id
    assert workspace.results_table.item(0, 1).text() == 'SINGLE'
    assert workspace.results_table.item(0, 2).text() == 'Charizard ex'
    assert workspace.results_table.item(0, 7).text() == 'ALIAS'
    assert workspace.status_label.text() == '1 product found.'


def test_workspace_empty_and_unmatched_searches_fail_safely(tmp_path):
    workspace, _ = _workspace(tmp_path)

    workspace.refresh_results()
    assert workspace.results_table.rowCount() == 0
    assert workspace.status_label.text() == 'Enter a search term to inspect registered products.'

    workspace.search_input.setText('not-a-product')
    workspace.refresh_results()
    assert workspace.results_table.rowCount() == 0
    assert workspace.status_label.text() == 'No registered products matched this search.'


def test_workspace_type_filter_is_applied_without_mutating_authority(tmp_path):
    workspace, _ = _workspace(tmp_path)
    before = workspace.lookup_service.database.connect().execute(
        'SELECT COUNT(*) FROM event_identity'
    ).fetchone()[0]

    workspace.search_input.setText('Charizard')
    workspace.product_type_filter.setCurrentIndex(2)
    workspace.refresh_results()

    after = workspace.lookup_service.database.connect().execute(
        'SELECT COUNT(*) FROM event_identity'
    ).fetchone()[0]
    assert workspace.results_table.rowCount() == 0
    assert before == after
