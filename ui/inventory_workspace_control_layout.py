from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget


INVENTORY_WORKSPACE_CONTROLS_VISUAL_CONTRACT = "m1.20c-inventory-workspace-controls"


class InventoryWorkspaceControlLayout(QWidget):
    """Compact two-row shell for the existing Inventory workspace controls."""

    def __init__(
        self,
        *,
        action_widgets: tuple[QWidget, ...],
        search_widget: QWidget,
        filter_widget: QWidget | tuple[QWidget, ...],
        sort_widget: QWidget,
        sort_order_widget: QWidget,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("visualContract", INVENTORY_WORKSPACE_CONTROLS_VISUAL_CONTRACT)
        self.setProperty("dashboardRole", "inventory-workspace-controls")
        self.setAccessibleName("Inventory workspace actions, search, filter, and sorting controls.")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(8)
        actions.addWidget(QLabel("📦 INVENTORY"))
        actions.addStretch(1)
        for widget in action_widgets:
            actions.addWidget(widget)
        root.addLayout(actions)
        self.action_layout = actions

        query = QHBoxLayout()
        query.setContentsMargins(0, 0, 0, 0)
        query.setSpacing(8)
        query.addWidget(search_widget, 1)
        for index, widget in enumerate(filter_widget if isinstance(filter_widget, tuple) else (filter_widget,)):
            if isinstance(filter_widget, tuple): query.addWidget(QLabel('Category' if index == 0 else 'Condition'))
            query.addWidget(widget)
        query.addWidget(QLabel("Sort by"))
        query.addWidget(sort_widget)
        query.addWidget(sort_order_widget)
        root.addLayout(query)

    def indexOf(self, widget: QWidget) -> int:
        """Preserve the legacy action-row layout contract for feature installers."""
        return self.action_layout.indexOf(widget)

    def insertWidget(self, index: int, widget: QWidget, *args) -> None:
        """Insert feature-owned controls into the compact action row."""
        self.action_layout.insertWidget(index, widget, *args)
