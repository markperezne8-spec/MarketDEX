import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import pytest
from PySide6.QtWidgets import QApplication, QStackedWidget, QWidget

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
    assert host.navigation_titles == ('Inventory', 'Pricing')
    assert [button.text() for button in host.navigation_buttons] == [
        'Inventory',
        'Pricing',
    ]
    assert [
        button.property('workspaceId') for button in host.navigation_buttons
    ] == ['inventory', 'pricing']
    host.activate('pricing')
    assert host.currentWidget() is host.workspace_widget('pricing')
    assert host.currentIndex() == host.workspace_indexes['pricing']
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


def test_workspace_host_exposes_navigation_rail_shell_contract():
    app = QApplication.instance() or QApplication([])
    host = WorkspaceHost(WorkspaceRegistry())

    assert host.objectName() == 'marketdexApplicationShell'
    assert host.accessibleName() == 'MarketDEX workspaces'
    assert host.navigation_rail.objectName() == 'marketdexNavigationRail'
    assert host.workspace_frame.objectName() == 'marketdexWorkspaceFrame'
    assert host.status_bar.objectName() == 'marketdexStatusBar'
    assert isinstance(host.workspace_stack, QStackedWidget)
    assert host.workspace_stack.objectName() == 'marketdexWorkspaceStack'
    assert host.navigation_badge.objectName() == 'marketdexNavigationBadge'
    assert host.navigation_badge.text() == 'COMMAND RAIL'
    assert host.navigation_rail.accessibleName() == (
        'MarketDEX command navigation rail'
    )
    assert host.navigation_visual_contract == 'm1.14d-north-star-left-navigation'
    assert host.documentMode() is True
    assert host.isMovable() is False
    assert host.tabsClosable() is False
    assert host.tabBar().expanding() is False
    assert '#2579D8' in host.styleSheet()
    assert '#FFD12E' in host.styleSheet()
    host.close()


def test_workspace_host_north_star_navigation_visuals_preserve_routes():
    app = QApplication.instance() or QApplication([])
    registry = WorkspaceRegistry()
    registry.register(WorkspaceDefinition('inventory', 'Inventory', _widget, order=10))
    registry.register(WorkspaceDefinition('pricing', 'Pricing', _widget, order=20))
    registry.register(
        WorkspaceDefinition(
            'listing-workflow',
            'Listing Workflow',
            _widget,
            order=30,
        )
    )
    host = WorkspaceHost(registry)

    host.mount_registered_workspaces()

    assert host.workspace_ids == ('inventory', 'pricing', 'listing-workflow')
    assert host.navigation_titles == (
        'Inventory',
        'Pricing',
        'Listing Workflow',
    )
    assert [button.text() for button in host.navigation_buttons] == [
        'Inventory',
        'Pricing',
        'Listing Workflow',
    ]
    assert [
        button.property('northStarRole') for button in host.navigation_buttons
    ] == ['workspace-navigation'] * 3
    assert [
        button.property('workspaceId') for button in host.navigation_buttons
    ] == ['inventory', 'pricing', 'listing-workflow']
    assert [button.accessibleName() for button in host.navigation_buttons] == [
        'Open Inventory workspace',
        'Open Pricing workspace',
        'Open Listing Workflow workspace',
    ]
    assert all(button.isCheckable() for button in host.navigation_buttons)
    assert not any('new-workspace' in button.text() for button in host.navigation_buttons)
    host.close()
