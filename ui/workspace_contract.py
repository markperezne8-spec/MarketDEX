from dataclasses import dataclass
from typing import Callable

from PySide6.QtWidgets import QWidget


@dataclass(frozen=True)
class WorkspaceDefinition:
    """Canonical metadata and factory contract for a MarketDEX shell workspace."""

    workspace_id: str
    title: str
    factory: Callable[[], QWidget]
    order: int = 100

    def __post_init__(self):
        if not self.workspace_id or not self.workspace_id.strip():
            raise ValueError('workspace_id is required')
        if not self.title or not self.title.strip():
            raise ValueError('workspace title is required')
        if not callable(self.factory):
            raise TypeError('workspace factory must be callable')
