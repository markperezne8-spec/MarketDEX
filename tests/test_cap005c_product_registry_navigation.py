import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication

from composition.application_composition import ApplicationComposition
from services.product_registry_lookup_service import ProductRegistryLookupService
from ui.product_registry_workspace import ProductRegistryWorkspace
from ui.shell_workspace_catalog import PRODUCT_REGISTRY_WORKSPACE_ID


def test_application_composition_mounts_product_registry_in_shell_order(tmp_path):
    app = QApplication.instance() or QApplication([])
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    window = composition.build_main_window()

    assert isinstance(composition.product_registry_lookup, ProductRegistryLookupService)
    assert isinstance(window.product_registry_workspace, ProductRegistryWorkspace)
    assert window.workspace_host.workspace_ids == (
        'inventory',
        PRODUCT_REGISTRY_WORKSPACE_ID,
        'collection-position',
        'pricing',
        'listing-workflow',
    )
    assert [
        window.workspace_host.tabText(index)
        for index in range(window.workspace_host.count())
    ] == ['Inventory', 'Product Registry', 'Collection Overview', 'Pricing', 'Listing Workflow']
    window.close()


def test_product_registry_navigation_uses_stable_workspace_identity(tmp_path):
    app = QApplication.instance() or QApplication([])
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')
    window = composition.build_main_window()

    window.workspace_host.activate(PRODUCT_REGISTRY_WORKSPACE_ID)

    assert window.workspace_host.currentWidget() is window.product_registry_workspace
    assert window.workspace_host.workspace_widget(
        PRODUCT_REGISTRY_WORKSPACE_ID
    ) is window.product_registry_workspace
    assert window.workspace_host.workspace_context.text() == 'PRODUCT REGISTRY'
    assert window.workspace_host.status_message.text() == (
        'Product Registry workspace active'
    )
    window.close()


def test_product_registry_navigation_remains_read_only(tmp_path):
    app = QApplication.instance() or QApplication([])
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')
    window = composition.build_main_window()

    with composition.product_registry_lookup.database.read_connection() as connection:
        before = {
            table: connection.execute(f'SELECT COUNT(*) n FROM {table}').fetchone()['n']
            for table in ('products', 'product_aliases', 'event_identity', 'audit_events')
        }

    window.workspace_host.activate(PRODUCT_REGISTRY_WORKSPACE_ID)
    window.product_registry_workspace.search_input.setText('not-present')
    window.product_registry_workspace.refresh_results()

    with composition.product_registry_lookup.database.read_connection() as connection:
        after = {
            table: connection.execute(f'SELECT COUNT(*) n FROM {table}').fetchone()['n']
            for table in ('products', 'product_aliases', 'event_identity', 'audit_events')
        }

    assert after == before
    window.close()
