import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import pytest
from PySide6.QtWidgets import QApplication, QWidget

from ui.shell_workspace_catalog import (
    INVENTORY_WORKSPACE_ID,
    LISTING_WORKFLOW_WORKSPACE_ID,
    PRICING_WORKSPACE_ID,
    register_core_shell_workspaces,
)
from ui.workspace_registry import WorkspaceRegistry


def _pages():
    return {
        INVENTORY_WORKSPACE_ID: QWidget(),
        PRICING_WORKSPACE_ID: QWidget(),
        LISTING_WORKFLOW_WORKSPACE_ID: QWidget(),
    }


def test_core_shell_catalog_registers_one_deterministic_workspace_set():
    app = QApplication.instance() or QApplication([])
    registry = WorkspaceRegistry()
    pages = _pages()

    register_core_shell_workspaces(registry, pages)

    assert [workspace.workspace_id for workspace in registry.all()] == [
        INVENTORY_WORKSPACE_ID,
        PRICING_WORKSPACE_ID,
        LISTING_WORKFLOW_WORKSPACE_ID,
    ]
    assert [workspace.title for workspace in registry.all()] == [
        'Inventory',
        'Pricing',
        'Listing Workflow',
    ]
    assert [workspace.factory() for workspace in registry.all()] == [
        pages[INVENTORY_WORKSPACE_ID],
        pages[PRICING_WORKSPACE_ID],
        pages[LISTING_WORKFLOW_WORKSPACE_ID],
    ]


def test_core_shell_catalog_fails_closed_for_incomplete_or_unexpected_pages():
    app = QApplication.instance() or QApplication([])

    with pytest.raises(KeyError, match='missing shell workspace pages'):
        register_core_shell_workspaces(
            WorkspaceRegistry(),
            {INVENTORY_WORKSPACE_ID: QWidget()},
        )

    pages = _pages()
    pages['unexpected'] = QWidget()
    with pytest.raises(KeyError, match='unexpected shell workspace pages'):
        register_core_shell_workspaces(WorkspaceRegistry(), pages)
