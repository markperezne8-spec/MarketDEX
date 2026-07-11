from __future__ import annotations

from ui.design_system.tokens import ColorRole, MarketDEXDesignTokens


def build_marketdex_qss(tokens: MarketDEXDesignTokens) -> str:
    """Build the canonical desktop QSS from semantic design tokens.

    The adapter is intentionally free of business logic. It translates the shared
    token set into Qt selectors used by reusable MarketDEX components and standard
    desktop controls.
    """

    tokens.validate()
    color = tokens.color
    radius = tokens.corner_radii
    border = tokens.border_widths
    standard = tokens.densities[next(d for d in tokens.densities if d.value == "standard")]

    return f"""
    QMainWindow, QWidget#marketdexAppRoot {{
        background: {color(ColorRole.APP_BACKGROUND)};
        color: {color(ColorRole.TEXT_PRIMARY)};
    }}

    QWidget {{
        color: {color(ColorRole.TEXT_PRIMARY)};
    }}

    QFrame#marketdexShell,
    QFrame#marketdexWorkspaceHeader,
    QFrame#marketdexDashboardPanel,
    QFrame#marketdexKpiCard,
    QFrame#marketdexStatePanel {{
        background: {color(ColorRole.SURFACE_PRIMARY)};
        border: {border['standard']}px solid {color(ColorRole.BORDER_SUBTLE)};
        border-radius: {radius['panel']}px;
    }}

    QFrame#marketdexWorkspaceHeader {{
        background: {color(ColorRole.SHELL_BACKGROUND)};
        border-color: {color(ColorRole.BORDER_STRONG)};
    }}

    QFrame#marketdexKpiCard:hover,
    QFrame#marketdexDashboardPanel:hover {{
        border-color: {color(ColorRole.BORDER_STRONG)};
    }}

    QLabel#marketdexWorkspaceTitle {{
        color: {color(ColorRole.TEXT_PRIMARY)};
        font-size: 20pt;
        font-weight: 700;
    }}

    QLabel#marketdexWorkspaceSubtitle,
    QLabel#marketdexPanelDescription,
    QLabel#marketdexKpiEvidence,
    QLabel#marketdexStateDetail {{
        color: {color(ColorRole.TEXT_SECONDARY)};
    }}

    QLabel#marketdexPanelTitle,
    QLabel#marketdexKpiLabel {{
        color: {color(ColorRole.TEXT_SECONDARY)};
        font-weight: 700;
    }}

    QLabel#marketdexKpiValue {{
        color: {color(ColorRole.TEXT_PRIMARY)};
        font-size: 22pt;
        font-weight: 700;
    }}

    QLabel#marketdexKpiComparison[direction="positive"] {{
        color: {color(ColorRole.POSITIVE)};
    }}

    QLabel#marketdexKpiComparison[direction="negative"] {{
        color: {color(ColorRole.NEGATIVE)};
    }}

    QLabel#marketdexKpiComparison[direction="neutral"] {{
        color: {color(ColorRole.TEXT_MUTED)};
    }}

    QLabel#marketdexStatusBadge {{
        border-radius: {radius['pill']}px;
        padding: 3px 9px;
        font-weight: 700;
    }}

    QLabel#marketdexStatusBadge[tone="information"] {{
        background: {color(ColorRole.SURFACE_INTERACTIVE)};
        color: {color(ColorRole.INFORMATION)};
        border: 1px solid {color(ColorRole.INFORMATION)};
    }}

    QLabel#marketdexStatusBadge[tone="positive"] {{
        background: {color(ColorRole.SURFACE_SECONDARY)};
        color: {color(ColorRole.POSITIVE)};
        border: 1px solid {color(ColorRole.POSITIVE)};
    }}

    QLabel#marketdexStatusBadge[tone="warning"] {{
        background: {color(ColorRole.SURFACE_SECONDARY)};
        color: {color(ColorRole.WARNING)};
        border: 1px solid {color(ColorRole.WARNING)};
    }}

    QLabel#marketdexStatusBadge[tone="negative"] {{
        background: {color(ColorRole.SURFACE_SECONDARY)};
        color: {color(ColorRole.NEGATIVE)};
        border: 1px solid {color(ColorRole.NEGATIVE)};
    }}

    QLabel#marketdexStatusBadge[tone="collection"] {{
        background: {color(ColorRole.SURFACE_SECONDARY)};
        color: {color(ColorRole.COLLECTION)};
        border: 1px solid {color(ColorRole.COLLECTION)};
    }}

    QPushButton {{
        min-height: {standard.control_height}px;
        padding: 0 12px;
        border-radius: {radius['control']}px;
        border: 1px solid {color(ColorRole.BORDER_STRONG)};
        background: {color(ColorRole.SURFACE_INTERACTIVE)};
        color: {color(ColorRole.TEXT_PRIMARY)};
        font-weight: 600;
    }}

    QPushButton:hover {{
        background: {color(ColorRole.PRIMARY_ACTION_HOVER)};
    }}

    QPushButton:pressed {{
        background: {color(ColorRole.PRIMARY_ACTION)};
    }}

    QPushButton:disabled {{
        background: {color(ColorRole.SURFACE_SECONDARY)};
        border-color: {color(ColorRole.DISABLED)};
        color: {color(ColorRole.DISABLED)};
    }}

    QPushButton#marketdexPrimaryButton {{
        background: {color(ColorRole.PRIMARY_ACTION)};
        border-color: {color(ColorRole.PRIMARY_ACTION)};
    }}

    QPushButton#marketdexOpportunityButton {{
        background: {color(ColorRole.OPPORTUNITY)};
        border-color: {color(ColorRole.OPPORTUNITY)};
        color: {color(ColorRole.APP_BACKGROUND)};
    }}

    QPushButton#marketdexDangerButton {{
        background: {color(ColorRole.NEGATIVE)};
        border-color: {color(ColorRole.NEGATIVE)};
    }}

    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
        min-height: {standard.control_height}px;
        padding: 0 9px;
        border-radius: {radius['control']}px;
        border: 1px solid {color(ColorRole.BORDER_SUBTLE)};
        background: {color(ColorRole.SURFACE_SECONDARY)};
        color: {color(ColorRole.TEXT_PRIMARY)};
        selection-background-color: {color(ColorRole.PRIMARY_ACTION)};
    }}

    QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
    QDoubleSpinBox:focus, QDateEdit:focus, QPushButton:focus,
    QTableView:focus, QTableWidget:focus {{
        border: {border['focus']}px solid {color(ColorRole.FOCUS_RING)};
    }}

    QTableView, QTableWidget {{
        background: {color(ColorRole.SURFACE_PRIMARY)};
        alternate-background-color: {color(ColorRole.SURFACE_SECONDARY)};
        color: {color(ColorRole.TEXT_PRIMARY)};
        gridline-color: {color(ColorRole.BORDER_SUBTLE)};
        border: 1px solid {color(ColorRole.BORDER_SUBTLE)};
        border-radius: {radius['panel']}px;
        selection-background-color: {color(ColorRole.SURFACE_INTERACTIVE)};
        selection-color: {color(ColorRole.TEXT_PRIMARY)};
    }}

    QHeaderView::section {{
        background: {color(ColorRole.SHELL_BACKGROUND)};
        color: {color(ColorRole.TEXT_SECONDARY)};
        border: none;
        border-right: 1px solid {color(ColorRole.BORDER_SUBTLE)};
        border-bottom: 1px solid {color(ColorRole.BORDER_STRONG)};
        padding: 7px 9px;
        font-weight: 700;
    }}

    QToolTip {{
        background: {color(ColorRole.SURFACE_ELEVATED)};
        color: {color(ColorRole.TEXT_PRIMARY)};
        border: 1px solid {color(ColorRole.BORDER_STRONG)};
        padding: 5px;
    }}

    QScrollBar:vertical, QScrollBar:horizontal {{
        background: {color(ColorRole.SHELL_BACKGROUND)};
        border: none;
    }}

    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
        background: {color(ColorRole.BORDER_STRONG)};
        border-radius: {radius['control']}px;
        min-height: 24px;
        min-width: 24px;
    }}
    """.strip()
