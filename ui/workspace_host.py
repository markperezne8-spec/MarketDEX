from types import MappingProxyType
from typing import Mapping

from PySide6.QtWidgets import QTabWidget, QWidget

from ui.workspace_registry import WorkspaceRegistry


class WorkspaceHost(QTabWidget):
    """Owns top-level workspace mounting, navigation, and shell presentation."""

    def __init__(self, registry: WorkspaceRegistry, parent=None):
        super().__init__(parent)
        self._registry = registry
        self._workspace_indexes: dict[str, int] = {}
        self._mounted = False

        self.setObjectName('marketdexWorkspaceHost')
        self.setAccessibleName('MarketDEX workspaces')
        self.setDocumentMode(True)
        self.setMovable(False)
        self.setTabsClosable(False)
        self.tabBar().setExpanding(False)
        self.setStyleSheet(
            """
            QTabWidget#marketdexWorkspaceHost::pane {
                border: 1px solid #d7dee8;
                background: #f7f9fc;
                top: -1px;
            }
            QTabWidget#marketdexWorkspaceHost QTabBar::tab {
                background: #e9eef5;
                border: 1px solid #d7dee8;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                color: #334155;
                font-size: 13px;
                font-weight: 600;
                margin-right: 4px;
                min-width: 120px;
                padding: 9px 18px;
            }
            QTabWidget#marketdexWorkspaceHost QTabBar::tab:hover {
                background: #dfe7f1;
                color: #0f172a;
            }
            QTabWidget#marketdexWorkspaceHost QTabBar::tab:selected {
                background: #ffffff;
                border-top: 3px solid #2563eb;
                color: #0f172a;
                padding-top: 7px;
            }
            """
        )

    @property
    def registry(self) -> WorkspaceRegistry:
        return self._registry

    @property
    def workspace_indexes(self) -> Mapping[str, int]:
        return MappingProxyType(self._workspace_indexes)

    @property
    def workspace_ids(self) -> tuple[str, ...]:
        return tuple(self._workspace_indexes)

    def mount_registered_workspaces(self) -> None:
        if self._mounted:
            raise RuntimeError('workspace host is already mounted')

        for workspace in self._registry.all():
            page = workspace.factory()
            if not isinstance(page, QWidget):
                raise TypeError(
                    f'workspace factory must return QWidget: {workspace.workspace_id}'
                )
            self._workspace_indexes[workspace.workspace_id] = self.addTab(
                page,
                workspace.title,
            )

        self._mounted = True

    def activate(self, workspace_id: str) -> None:
        try:
            index = self._workspace_indexes[workspace_id]
        except KeyError as exc:
            raise KeyError(f'unknown shell workspace: {workspace_id}') from exc
        self.setCurrentIndex(index)

    def workspace_widget(self, workspace_id: str) -> QWidget:
        try:
            index = self._workspace_indexes[workspace_id]
        except KeyError as exc:
            raise KeyError(f'unknown shell workspace: {workspace_id}') from exc
        return self.widget(index)
