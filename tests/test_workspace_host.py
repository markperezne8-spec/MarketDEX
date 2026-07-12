import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import pytest
from PySide6.QtWidgets import QApplication, QWidget

from ui.workspace_contract import WorkspaceDefinition
from ui.workspace_host import WorkspaceHost
from ui.workspace_registry import WorkspaceRegistry


def _widget():
    return QWidget()


def test_workspace_host_mounts_registry_order_and_activates_by_identity():
    app = QApplication.instance() or QApplication([])
    registry = WorkspaceRegistry()
    registry.register(WorkspaceDefinition('pricing', 'Pricing', _widget, order=20))
    registry.register(WorkspaceDefinition('inventory', 'Inventory', _widget, order=10))
    host = WorkspaceHost(registry)

    host.mount_registered_workspaces()

    assert host.workspace_ids == ('inventory', 'pricing')
    assert [host.tabText(index) for index in range(host.count())] == [
        'Inventory',
        'Pricing',
    ]
    host.activate('pricing')
    assert host.currentWidget() is host.workspace_widget('pricing')
    host.close()


def test_workspace_host_rejects_unknown_navigation_and_duplicate_mounting():
    app = QApplication.instance() or QApplication([])
    registry = WorkspaceRegistry()
    registry.register(WorkspaceDefinition('inventory', 'Inventory', _widget))
    host = WorkspaceHost(registry)
    host.mount_registered_workspaces()

    with pytest.raises(KeyError, match='unknown shell workspace'):
        host.activate('missing')
    with pytest.raises(RuntimeError, match='already mounted'):
        host.mount_registered_workspaces()
    host.close()


def test_workspace_host_rejects_factory_results_that_are_not_widgets():
    app = QApplication.instance() or QApplication([])
    registry = WorkspaceRegistry()
    registry.register(
        WorkspaceDefinition('invalid', 'Invalid', lambda: object())
    )
    host = WorkspaceHost(registry)

    with pytest.raises(TypeError, match='factory must return QWidget'):
        host.mount_registered_workspaces()
    host.close()


def test_workspace_host_exposes_professional_shell_presentation_contract():
    app = QApplication.instance() or QApplication([])
    host = WorkspaceHost(WorkspaceRegistry())

    assert host.objectName() == 'marketdexWorkspaceHost'
    assert host.accessibleName() == 'MarketDEX workspaces'
    assert host.documentMode() is True
    assert host.isMovable() is False
    assert host.tabsClosable() is False
    assert host.tabBar().expanding() is False
    assert '#2563eb' in host.styleSheet()
    host.close()
