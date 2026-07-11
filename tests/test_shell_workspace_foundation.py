import pytest
from PySide6.QtWidgets import QWidget

from ui.workspace_contract import WorkspaceDefinition
from ui.workspace_registry import WorkspaceRegistry


def _widget():
    return QWidget()


def test_workspace_registry_orders_modules_without_shell_specific_code():
    registry = WorkspaceRegistry()
    registry.register(WorkspaceDefinition('inventory', 'Inventory', _widget, order=20))
    registry.register(WorkspaceDefinition('mission-control', 'Mission Control', _widget, order=10))
    registry.register(WorkspaceDefinition('grading-lab', 'Grading Lab', _widget, order=30))

    assert [item.workspace_id for item in registry.all()] == [
        'mission-control',
        'inventory',
        'grading-lab',
    ]


def test_workspace_registry_rejects_competing_workspace_identity():
    registry = WorkspaceRegistry()
    registry.register(WorkspaceDefinition('inventory', 'Inventory', _widget))

    with pytest.raises(ValueError, match='duplicate workspace_id'):
        registry.register(WorkspaceDefinition('inventory', 'Other Inventory', _widget))


def test_workspace_contract_rejects_invalid_modules():
    with pytest.raises(ValueError, match='workspace_id'):
        WorkspaceDefinition('', 'Inventory', _widget)
    with pytest.raises(ValueError, match='title'):
        WorkspaceDefinition('inventory', '', _widget)
    with pytest.raises(TypeError, match='factory'):
        WorkspaceDefinition('inventory', 'Inventory', None)
