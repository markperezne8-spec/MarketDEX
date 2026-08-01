from PySide6.QtWidgets import QComboBox, QLineEdit, QPushButton

from ui.inventory_workspace_control_layout import (
    INVENTORY_WORKSPACE_CONTROLS_VISUAL_CONTRACT,
    InventoryWorkspaceControlLayout,
)


def test_inventory_workspace_control_layout_preserves_supplied_controls(qtbot) -> None:
    actions = (QPushButton("Import CSV"), QPushButton("+ Add Asset"))
    search = QLineEdit()
    asset_filter = QComboBox()
    sort = QComboBox()
    order = QComboBox()

    shell = InventoryWorkspaceControlLayout(
        action_widgets=actions,
        search_widget=search,
        filter_widget=asset_filter,
        sort_widget=sort,
        sort_order_widget=order,
    )
    qtbot.addWidget(shell)

    assert shell.property("visualContract") == INVENTORY_WORKSPACE_CONTROLS_VISUAL_CONTRACT
    assert shell.property("dashboardRole") == "inventory-workspace-controls"
    assert all(widget.parent() is shell for widget in (*actions, search, asset_filter, sort, order))
