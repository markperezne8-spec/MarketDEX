from ui.workspace_contract import WorkspaceDefinition


class WorkspaceRegistry:
    """Single shell authority for workspace registration and discovery."""

    def __init__(self):
        self._workspaces = {}

    def register(self, workspace: WorkspaceDefinition) -> None:
        if workspace.workspace_id in self._workspaces:
            raise ValueError(f'duplicate workspace_id: {workspace.workspace_id}')
        self._workspaces[workspace.workspace_id] = workspace

    def get(self, workspace_id: str) -> WorkspaceDefinition:
        try:
            return self._workspaces[workspace_id]
        except KeyError as exc:
            raise KeyError(f'unknown workspace_id: {workspace_id}') from exc

    def all(self) -> tuple[WorkspaceDefinition, ...]:
        return tuple(sorted(self._workspaces.values(), key=lambda item: (item.order, item.title, item.workspace_id)))

    def __contains__(self, workspace_id: str) -> bool:
        return workspace_id in self._workspaces

    def __len__(self) -> int:
        return len(self._workspaces)
