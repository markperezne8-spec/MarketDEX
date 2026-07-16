from types import MappingProxyType
from typing import Mapping

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.tokens import ColorRole, build_visual_north_star_tokens
from ui.workspace_registry import WorkspaceRegistry


class _NavigationRailContract:
    """Compatibility surface for the former tab-bar presentation contract."""

    def __init__(self) -> None:
        self._expanding = False

    def setExpanding(self, expanding: bool) -> None:
        self._expanding = bool(expanding)

    def expanding(self) -> bool:
        return self._expanding


class WorkspaceHost(QWidget):
    """Canonical MarketDEX shell with persistent navigation and stacked workspaces."""

    currentChanged = Signal(int)

    def __init__(self, registry: WorkspaceRegistry, parent=None):
        super().__init__(parent)
        self._registry = registry
        self._workspace_indexes: dict[str, int] = {}
        self._workspace_titles: list[str] = []
        self._navigation_buttons: list[QPushButton] = []
        self._mounted = False
        self._document_mode = True
        self._movable = False
        self._tabs_closable = False
        self._tab_bar_contract = _NavigationRailContract()

        self.setObjectName('marketdexApplicationShell')
        self.setAccessibleName('MarketDEX workspaces')

        shell_layout = QHBoxLayout(self)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        self.navigation_rail = QFrame(self)
        self.navigation_rail.setObjectName('marketdexNavigationRail')
        self.navigation_rail.setAccessibleName('MarketDEX command navigation rail')
        self.navigation_rail.setFixedWidth(248)
        navigation_layout = QVBoxLayout(self.navigation_rail)
        navigation_layout.setContentsMargins(18, 22, 18, 16)
        navigation_layout.setSpacing(9)

        brand = QLabel('MarketDEX OS', self.navigation_rail)
        brand.setObjectName('marketdexShellBrand')
        brand.setAccessibleName('MarketDEX OS brand')
        brand.setWordWrap(True)
        navigation_layout.addWidget(brand)

        mode = QLabel('BUSINESS OPERATING SYSTEM', self.navigation_rail)
        mode.setObjectName('marketdexShellMode')
        mode.setAccessibleName('Business operating system mode')
        mode.setWordWrap(True)
        navigation_layout.addWidget(mode)

        self.navigation_badge = QLabel('COMMAND RAIL', self.navigation_rail)
        self.navigation_badge.setObjectName('marketdexNavigationBadge')
        self.navigation_badge.setAccessibleName('North Star command rail visual marker')
        navigation_layout.addWidget(self.navigation_badge)

        section = QLabel('WORKSPACES', self.navigation_rail)
        section.setObjectName('marketdexNavigationSection')
        section.setAccessibleName('Workspace navigation section')
        navigation_layout.addSpacing(10)
        navigation_layout.addWidget(section)

        self.navigation_items = QVBoxLayout()
        self.navigation_items.setSpacing(6)
        navigation_layout.addLayout(self.navigation_items)
        navigation_layout.addStretch(1)

        self.navigation_status = QLabel('● LOCAL AUTHORITY\nSQLite • Offline First', self.navigation_rail)
        self.navigation_status.setObjectName('marketdexNavigationStatus')
        self.navigation_status.setAccessibleName('Local authority status: SQLite offline first')
        self.navigation_status.setWordWrap(True)
        navigation_layout.addWidget(self.navigation_status)

        self.workspace_frame = QFrame(self)
        self.workspace_frame.setObjectName('marketdexWorkspaceFrame')
        workspace_layout = QVBoxLayout(self.workspace_frame)
        workspace_layout.setContentsMargins(18, 14, 18, 12)
        workspace_layout.setSpacing(10)

        self.workspace_context = QLabel('MISSION CONTROL', self.workspace_frame)
        self.workspace_context.setObjectName('marketdexWorkspaceContext')
        workspace_layout.addWidget(self.workspace_context)

        self.workspace_stack = QStackedWidget(self.workspace_frame)
        self.workspace_stack.setObjectName('marketdexWorkspaceStack')
        self.workspace_stack.currentChanged.connect(self._sync_navigation_state)
        self.workspace_stack.currentChanged.connect(self.currentChanged.emit)
        workspace_layout.addWidget(self.workspace_stack, 1)

        self.status_bar = QFrame(self.workspace_frame)
        self.status_bar.setObjectName('marketdexStatusBar')
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(12, 7, 12, 7)
        self.status_message = QLabel('MarketDEX ready', self.status_bar)
        self.status_message.setObjectName('marketdexStatusMessage')
        status_layout.addWidget(self.status_message)
        status_layout.addStretch(1)
        self.status_mode = QLabel('OFFLINE FIRST', self.status_bar)
        self.status_mode.setObjectName('marketdexStatusMode')
        status_layout.addWidget(self.status_mode)
        workspace_layout.addWidget(self.status_bar)

        shell_layout.addWidget(self.navigation_rail)
        shell_layout.addWidget(self.workspace_frame, 1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setStyleSheet(_build_workspace_host_qss())

    @property
    def navigation_buttons(self) -> tuple[QPushButton, ...]:
        return tuple(self._navigation_buttons)

    @property
    def navigation_titles(self) -> tuple[str, ...]:
        return tuple(self._workspace_titles)

    @property
    def navigation_visual_contract(self) -> str:
        return 'm1.14d-north-star-left-navigation'

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

        resolved_pages: list[tuple[str, str, QWidget]] = []
        for workspace in self._registry.all():
            page = workspace.factory()
            if not isinstance(page, QWidget):
                raise TypeError(
                    f'workspace factory must return QWidget: {workspace.workspace_id}'
                )
            resolved_pages.append((workspace.workspace_id, workspace.title, page))

        for workspace_id, title, page in resolved_pages:
            self._workspace_indexes[workspace_id] = self.addTab(
                page,
                title,
                workspace_id,
            )

        self._mounted = True
        if self.count():
            self.setCurrentIndex(0)

    def addTab(self, page: QWidget, title: str, workspace_id: str | None = None) -> int:
        index = self.workspace_stack.addWidget(page)
        self._workspace_titles.append(title)
        button = QPushButton(title, self.navigation_rail)
        button.setObjectName('marketdexNavigationItem')
        button.setProperty('northStarRole', 'workspace-navigation')
        if workspace_id is not None:
            button.setProperty('workspaceId', workspace_id)
        button.setAccessibleName(f'Open {title} workspace')
        button.setCheckable(True)
        button.clicked.connect(lambda _checked=False, target=index: self.setCurrentIndex(target))
        self.navigation_items.addWidget(button)
        self._navigation_buttons.append(button)
        return index

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
        widget = self.widget(index)
        if widget is None:
            raise RuntimeError(f'workspace widget is unavailable: {workspace_id}')
        return widget

    def _sync_navigation_state(self, index: int) -> None:
        for button_index, button in enumerate(self._navigation_buttons):
            button.setChecked(button_index == index)
        if 0 <= index < len(self._workspace_titles):
            title = self._workspace_titles[index]
            self.workspace_context.setText(title.upper())
            self.status_message.setText(f'{title} workspace active')

    def setCurrentIndex(self, index: int) -> None:
        self.workspace_stack.setCurrentIndex(index)

    def currentWidget(self) -> QWidget | None:
        return self.workspace_stack.currentWidget()

    def currentIndex(self) -> int:
        return self.workspace_stack.currentIndex()

    def widget(self, index: int) -> QWidget | None:
        return self.workspace_stack.widget(index)

    def count(self) -> int:
        return self.workspace_stack.count()

    def tabText(self, index: int) -> str:
        return self._workspace_titles[index]

    def setDocumentMode(self, enabled: bool) -> None:
        self._document_mode = bool(enabled)

    def documentMode(self) -> bool:
        return self._document_mode

    def setMovable(self, movable: bool) -> None:
        self._movable = bool(movable)

    def isMovable(self) -> bool:
        return self._movable

    def setTabsClosable(self, closable: bool) -> None:
        self._tabs_closable = bool(closable)

    def tabsClosable(self) -> bool:
        return self._tabs_closable

    def tabBar(self) -> _NavigationRailContract:
        return self._tab_bar_contract


def _build_workspace_host_qss() -> str:
    tokens = build_visual_north_star_tokens()
    color = tokens.color
    radius = tokens.corner_radii
    border = tokens.border_widths
    return f"""
            QWidget#marketdexApplicationShell {{
                background: {color(ColorRole.APP_BACKGROUND)};
            }}
            QFrame#marketdexNavigationRail {{
                background: {color(ColorRole.SHELL_BACKGROUND)};
                border-right: {border['selected']}px solid {color(ColorRole.BORDER_STRONG)};
            }}
            QLabel#marketdexShellBrand {{
                color: {color(ColorRole.TEXT_PRIMARY)};
                font-size: 24px;
                font-weight: 800;
            }}
            QLabel#marketdexShellMode,
            QLabel#marketdexNavigationSection {{
                color: {color(ColorRole.INFORMATION)};
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 1px;
            }}
            QLabel#marketdexNavigationBadge {{
                background: {color(ColorRole.SURFACE_INTERACTIVE)};
                border: {border['standard']}px solid {color(ColorRole.BORDER_STRONG)};
                border-radius: {radius['pill']}px;
                color: {color(ColorRole.INFORMATION)};
                font-size: 10px;
                font-weight: 800;
                padding: 5px 10px;
            }}
            QPushButton#marketdexNavigationItem {{
                background: {color(ColorRole.SURFACE_PRIMARY)};
                border: {border['standard']}px solid {color(ColorRole.BORDER_SUBTLE)};
                border-left: {border['selected']}px solid transparent;
                border-radius: {radius['panel']}px;
                color: {color(ColorRole.TEXT_SECONDARY)};
                font-size: 13px;
                font-weight: 650;
                min-height: 40px;
                padding: 0 13px;
                text-align: left;
            }}
            QPushButton#marketdexNavigationItem:hover {{
                background: {color(ColorRole.SURFACE_INTERACTIVE)};
                border-color: {color(ColorRole.BORDER_STRONG)};
                color: {color(ColorRole.TEXT_PRIMARY)};
            }}
            QPushButton#marketdexNavigationItem:checked {{
                background: {color(ColorRole.SURFACE_INTERACTIVE)};
                border-color: {color(ColorRole.BORDER_STRONG)};
                border-left-color: {color(ColorRole.OPPORTUNITY)};
                color: {color(ColorRole.TEXT_PRIMARY)};
            }}
            QPushButton#marketdexNavigationItem:focus {{
                border-color: {color(ColorRole.FOCUS_RING)};
            }}
            QLabel#marketdexNavigationStatus {{
                background: {color(ColorRole.SURFACE_PRIMARY)};
                border: {border['standard']}px solid {color(ColorRole.POSITIVE)};
                border-radius: {radius['panel']}px;
                color: {color(ColorRole.POSITIVE)};
                font-size: 11px;
                padding: 10px;
            }}
            QFrame#marketdexWorkspaceFrame {{
                background: {color(ColorRole.APP_BACKGROUND)};
            }}
            QLabel#marketdexWorkspaceContext {{
                color: {color(ColorRole.TEXT_MUTED)};
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 1px;
            }}
            QStackedWidget#marketdexWorkspaceStack {{
                background: {color(ColorRole.APP_BACKGROUND)};
                border: {border['standard']}px solid {color(ColorRole.BORDER_SUBTLE)};
                border-radius: {radius['prominent']}px;
            }}
            QFrame#marketdexStatusBar {{
                background: {color(ColorRole.SURFACE_PRIMARY)};
                border: {border['standard']}px solid {color(ColorRole.BORDER_SUBTLE)};
                border-radius: {radius['panel']}px;
            }}
            QLabel#marketdexStatusMessage {{
                color: {color(ColorRole.TEXT_SECONDARY)};
                font-size: 11px;
            }}
            QLabel#marketdexStatusMode {{
                color: {color(ColorRole.INFORMATION)};
                font-size: 10px;
                font-weight: 800;
            }}
            """
