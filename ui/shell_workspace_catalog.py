from dataclasses import dataclass
from typing import Mapping

from PySide6.QtWidgets import QWidget

from ui.workspace_contract import WorkspaceDefinition
from ui.workspace_registry import WorkspaceRegistry


INVENTORY_WORKSPACE_ID = 'inventory'
PRICING_WORKSPACE_ID = 'pricing'
LISTING_WORKFLOW_WORKSPACE_ID = 'listing-workflow'


@dataclass(frozen=True)
class ShellWorkspaceSpec:
    workspace_id: str
    title: str
    order: int


CORE_SHELL_WORKSPACES = (
    ShellWorkspaceSpec(INVENTORY_WORKSPACE_ID, 'Inventory', 10),
    ShellWorkspaceSpec(PRICING_WORKSPACE_ID, 'Pricing', 20),
    ShellWorkspaceSpec(LISTING_WORKFLOW_WORKSPACE_ID, 'Listing Workflow', 30),
)


def register_core_shell_workspaces(
    registry: WorkspaceRegistry,
    pages: Mapping[str, QWidget],
) -> None:
    expected_ids = {spec.workspace_id for spec in CORE_SHELL_WORKSPACES}
    supplied_ids = set(pages)
    missing_ids = expected_ids - supplied_ids
    unexpected_ids = supplied_ids - expected_ids

    if missing_ids:
        raise KeyError(
            f'missing shell workspace pages: {", ".join(sorted(missing_ids))}'
        )
    if unexpected_ids:
        raise KeyError(
            f'unexpected shell workspace pages: {", ".join(sorted(unexpected_ids))}'
        )

    for spec in CORE_SHELL_WORKSPACES:
        page = pages[spec.workspace_id]
        if not isinstance(page, QWidget):
            raise TypeError(f'workspace page must be QWidget: {spec.workspace_id}')
        registry.register(
            WorkspaceDefinition(
                workspace_id=spec.workspace_id,
                title=spec.title,
                factory=lambda page=page: page,
                order=spec.order,
            )
        )
