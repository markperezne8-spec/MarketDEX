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
        filter_widget: QWidget,
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

        query = QHBoxLayout()
        query.setContentsMargins(0, 0, 0, 0)
        query.setSpacing(8)
        query.addWidget(search_widget, 1)
        query.addWidget(filter_widget)
        query.addWidget(QLabel("Sort by"))
        query.addWidget(sort_widget)
        query.addWidget(sort_order_widget)
        root.addLayout(query)
