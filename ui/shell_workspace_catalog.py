from dataclasses import dataclass
from typing import Mapping

from PySide6.QtWidgets import QWidget

from ui.workspace_contract import WorkspaceDefinition
from ui.workspace_registry import WorkspaceRegistry


INVENTORY_WORKSPACE_ID = 'inventory'
PRODUCT_REGISTRY_WORKSPACE_ID = 'product-registry'
COLLECTION_POSITION_WORKSPACE_ID = 'collection-position'
MARKET_INTELLIGENCE_WORKSPACE_ID = 'market-intelligence'
PRICING_WORKSPACE_ID = 'pricing'
LISTING_WORKFLOW_WORKSPACE_ID = 'listing-workflow'


@dataclass(frozen=True)
class ShellWorkspaceSpec:
    workspace_id: str
    title: str
    order: int


PRODUCT_REGISTRY_WORKSPACE = ShellWorkspaceSpec(
    PRODUCT_REGISTRY_WORKSPACE_ID,
    'Product Registry',
    15,
)
COLLECTION_POSITION_WORKSPACE = ShellWorkspaceSpec(
    COLLECTION_POSITION_WORKSPACE_ID,
    'Collection Overview',
    16,
)
MARKET_INTELLIGENCE_WORKSPACE = ShellWorkspaceSpec(
    MARKET_INTELLIGENCE_WORKSPACE_ID,
    'Market Intelligence',
    17,
)

CORE_SHELL_WORKSPACES = (
    ShellWorkspaceSpec(INVENTORY_WORKSPACE_ID, 'Inventory', 10),
    ShellWorkspaceSpec(PRICING_WORKSPACE_ID, 'Pricing', 20),
    ShellWorkspaceSpec(LISTING_WORKFLOW_WORKSPACE_ID, 'Listing Workflow', 30),
)


def register_product_registry_workspace(
    registry: WorkspaceRegistry,
    page: QWidget,
) -> None:
    if not isinstance(page, QWidget):
        raise TypeError('workspace page must be QWidget: product-registry')
    registry.register(
        WorkspaceDefinition(
            workspace_id=PRODUCT_REGISTRY_WORKSPACE.workspace_id,
            title=PRODUCT_REGISTRY_WORKSPACE.title,
            factory=lambda page=page: page,
            order=PRODUCT_REGISTRY_WORKSPACE.order,
        )
    )


def register_collection_position_workspace(
    registry: WorkspaceRegistry,
    page: QWidget,
) -> None:
    if not isinstance(page, QWidget):
        raise TypeError('workspace page must be QWidget: collection-position')
    registry.register(
        WorkspaceDefinition(
            workspace_id=COLLECTION_POSITION_WORKSPACE.workspace_id,
            title=COLLECTION_POSITION_WORKSPACE.title,
            factory=lambda page=page: page,
            order=COLLECTION_POSITION_WORKSPACE.order,
        )
    )


def register_market_intelligence_workspace(
    registry: WorkspaceRegistry,
    page: QWidget,
) -> None:
    if not isinstance(page, QWidget):
        raise TypeError('workspace page must be QWidget: market-intelligence')
    registry.register(
        WorkspaceDefinition(
            workspace_id=MARKET_INTELLIGENCE_WORKSPACE.workspace_id,
            title=MARKET_INTELLIGENCE_WORKSPACE.title,
            factory=lambda page=page: page,
            order=MARKET_INTELLIGENCE_WORKSPACE.order,
        )
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
