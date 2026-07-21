from __future__ import annotations

from PySide6.QtCore import QPoint, QTimer
from PySide6.QtWidgets import QScrollArea, QWidget

from ui.shell_workspace_catalog import INVENTORY_WORKSPACE_ID
from ui.workspace_host import WorkspaceHost


INVENTORY_WORKSPACE_FOCUS_CONTRACT = 'inventory-workspace-focus-v1'


def _inventory_anchor_index(window) -> int:
    panel_layout = window.inventory_panel.layout()
    inventory_header = getattr(window, 'inventory_header', None)
    if inventory_header is not None:
        for index in range(panel_layout.count()):
            item = panel_layout.itemAt(index)
            if item is not None and item.layout() is inventory_header:
                return index

    table_index = panel_layout.indexOf(window.inventory_table)
    return table_index if table_index >= 0 else panel_layout.count()


def install_inventory_workspace_focus_feature(window) -> None:
    """Focus the combined legacy page on Inventory when Inventory is activated."""
    host = getattr(window, 'workspace_host', None)
    scroll = getattr(window, 'marketdex_workspace_scroll', None)
    if not isinstance(host, WorkspaceHost):
        raise TypeError('workspace_host must be a WorkspaceHost')
    if not isinstance(scroll, QScrollArea):
        raise TypeError('marketdex_workspace_scroll must be a QScrollArea')

    panel_layout = window.inventory_panel.layout()
    anchor = QWidget(window.inventory_panel)
    anchor.setObjectName('marketdexInventoryWorkspaceAnchor')
    anchor.setProperty('visualContract', INVENTORY_WORKSPACE_FOCUS_CONTRACT)
    anchor.setFixedHeight(1)
    panel_layout.insertWidget(_inventory_anchor_index(window), anchor)

    inventory_index = host.workspace_indexes[INVENTORY_WORKSPACE_ID]

    def focus_inventory(index: int) -> None:
        if index != inventory_index:
            return

        def apply_focus() -> None:
            scroll_content = scroll.widget()
            if scroll_content is None:
                return
            target = anchor.mapTo(scroll_content, QPoint(0, 0)).y()
            bar = scroll.verticalScrollBar()
            bar.setValue(max(bar.minimum(), min(target, bar.maximum())))

        QTimer.singleShot(0, apply_focus)

    host.currentChanged.connect(focus_inventory)
    focus_inventory(host.currentIndex())

    window.inventory_workspace_anchor = anchor
    window.inventory_workspace_focus_contract = INVENTORY_WORKSPACE_FOCUS_CONTRACT
