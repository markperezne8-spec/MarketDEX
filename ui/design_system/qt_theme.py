from __future__ import annotations

from ui.design_system.tokens import (
    ColorRole,
    MarketDEXDesignTokens,
    NorthStarPanelTone,
)


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

    QFrame#marketdexKpiCard[dashboardRole="existing-kpi"] {{
        min-height: 72px;
        max-height: 86px;
    }}

    QFrame#marketdexKpiCard[dashboardRole="inventory-command-summary"] {{
        min-height: 92px;
        max-height: 108px;
    }}

    QFrame#marketdexDashboardPanel[dashboardRole="inventory-command-placeholder"] {{
        min-height: 92px;
        max-height: 112px;
    }}

    QFrame#marketdexWorkspaceHeader {{
        background: {color(ColorRole.SHELL_BACKGROUND)};
        border-color: {color(ColorRole.BORDER_STRONG)};
    }}

    QFrame#marketdexKpiCard:hover,
    QFrame#marketdexDashboardPanel:hover {{
        border-color: {color(ColorRole.BORDER_STRONG)};
    }}

    QFrame#marketdexDashboardPanel[northStarTone="{NorthStarPanelTone.COMMAND.value}"] {{
        background: {color(tokens.north_star_panel_tones[NorthStarPanelTone.COMMAND])};
        border-color: {color(ColorRole.BORDER_STRONG)};
    }}

    QFrame#marketdexDashboardPanel[northStarTone="{NorthStarPanelTone.SCOREBOARD.value}"] {{
        background: {color(ColorRole.SURFACE_PRIMARY)};
        border-color: {color(tokens.north_star_panel_tones[NorthStarPanelTone.SCOREBOARD])};
    }}

    QFrame#marketdexDashboardPanel[northStarTone="{NorthStarPanelTone.OPPORTUNITY.value}"] {{
        background: {color(ColorRole.SURFACE_PRIMARY)};
        border-color: {color(tokens.north_star_panel_tones[NorthStarPanelTone.OPPORTUNITY])};
    }}

    QFrame#marketdexDashboardPanel[northStarTone="{NorthStarPanelTone.RISK.value}"] {{
        background: {color(ColorRole.SURFACE_PRIMARY)};
        border-color: {color(tokens.north_star_panel_tones[NorthStarPanelTone.RISK])};
    }}

    QFrame#marketdexDashboardPanel[northStarTone="{NorthStarPanelTone.INVENTORY.value}"] {{
        background: {color(tokens.north_star_panel_tones[NorthStarPanelTone.INVENTORY])};
        border-color: {color(ColorRole.BORDER_STRONG)};
    }}

    QFrame#marketdexDashboardPanel[northStarTone="{NorthStarPanelTone.INTELLIGENCE.value}"] {{
        background: {color(ColorRole.SURFACE_PRIMARY)};
        border-color: {color(tokens.north_star_panel_tones[NorthStarPanelTone.INTELLIGENCE])};
    }}

    QLabel#marketdexWorkspaceTitle {{
        color: {color(ColorRole.TEXT_PRIMARY)};
        font-size: 20pt;
        font-weight: 700;
    }}

    QLabel#marketdexWorkspaceSubtitle,
    QLabel#marketdexPricingSubtitle,
    QLabel#workspaceHandoffGuidance,
    QLabel#marketdexPanelDescription,
    QLabel#marketdexKpiEvidence,
    QLabel#marketdexStateDetail {{
        color: {color(ColorRole.TEXT_SECONDARY)};
    }}

    QWidget#marketdexPricingWorkspace,
    QWidget#marketdexListingWorkspace {{
        background: {color(ColorRole.APP_BACKGROUND)};
    }}

    QWidget#marketdexListingWorkspace QGroupBox {{
        background: {color(ColorRole.SURFACE_PRIMARY)};
        border: {border['standard']}px solid {color(ColorRole.BORDER_SUBTLE)};
        border-radius: {radius['panel']}px;
        color: {color(ColorRole.TEXT_PRIMARY)};
        margin-top: 10px;
        padding-top: 10px;
    }}

    QWidget#marketdexListingWorkspace QGroupBox::title {{
        color: {color(ColorRole.TEXT_SECONDARY)};
        left: 12px;
        padding: 0 5px;
    }}

    QWidget#marketdexListingWorkspace QLabel {{
        color: {color(ColorRole.TEXT_PRIMARY)};
    }}

    QLabel#marketdexPricingTitle {{
        color: {color(ColorRole.TEXT_PRIMARY)};
        font-size: 20pt;
        font-weight: 700;
    }}

    QLabel#marketdexPricingSubtitle {{
        font-size: 10pt;
        font-weight: 600;
    }}

    QGroupBox#workspaceHandoffCard {{
        background: {color(ColorRole.SURFACE_PRIMARY)};
        border: {border['standard']}px solid {color(ColorRole.BORDER_SUBTLE)};
        border-radius: {radius['panel']}px;
        color: {color(ColorRole.TEXT_PRIMARY)};
        font-weight: 700;
        margin-top: 10px;
        padding-top: 10px;
    }}

    QGroupBox#workspaceHandoffCard::title {{
        color: {color(ColorRole.TEXT_SECONDARY)};
        left: 12px;
        padding: 0 5px;
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

    QWidget#collectionPositionWorkspace {{
        background: {color(ColorRole.APP_BACKGROUND)};
    }}

    QFrame#collectionPositionEmptyState {{
        background: {color(ColorRole.SURFACE_PRIMARY)};
        border: 1px solid {color(ColorRole.BORDER_STRONG)};
        border-radius: {radius['panel']}px;
    }}

    QLabel#collectionPositionEmptyStateTitle {{
        color: {color(ColorRole.TEXT_PRIMARY)};
        font-size: 12pt;
        font-weight: 700;
    }}

    QLabel#collectionPositionEmptyStateDetail {{
        color: {color(ColorRole.TEXT_SECONDARY)};
    }}

    QFrame#collectionPositionFieldAuthority {{
        background: {color(ColorRole.SURFACE_SECONDARY)};
        border: 1px solid {color(ColorRole.BORDER_SUBTLE)};
        border-radius: {radius['panel']}px;
    }}

    QLabel#collectionPositionFieldAuthorityTitle {{
        color: {color(ColorRole.TEXT_PRIMARY)};
        font-size: 12pt;
        font-weight: 700;
    }}

    QLabel#collectionPositionFieldAuthorityDetail {{
        color: {color(ColorRole.TEXT_SECONDARY)};
    }}

    QWidget#reportsWorkspace {{
        background: {color(ColorRole.APP_BACKGROUND)};
    }}

    QWidget#reportsScrollContent {{
        background: {color(ColorRole.APP_BACKGROUND)};
    }}

    QLabel#reportsTitle {{
        color: {color(ColorRole.TEXT_PRIMARY)};
        font-size: 20pt;
        font-weight: 700;
        padding-top: 4px;
    }}

    QFrame#reportsCatalogScopePanel {{
        background: {color(ColorRole.SURFACE_SECONDARY)};
        border: 1px solid {color(ColorRole.BORDER_SUBTLE)};
        border-radius: {radius['panel']}px;
    }}

    QLabel#reportsCatalogScopeTitle {{
        color: {color(ColorRole.TEXT_PRIMARY)};
        font-size: 12pt;
        font-weight: 700;
    }}

    QLabel#reportsInventoryAgeMode,
    QLabel#reportsInventoryTurnoverMode,
    QLabel#reportsPurchaseSourceMode {{
        color: {color(ColorRole.TEXT_MUTED)};
        font-size: 8pt;
        font-weight: 700;
        letter-spacing: 0.8px;
    }}

    QLabel#reportsSubtitle,
    QLabel#reportsStatusLabel,
    QLabel#reportsResultStatusLabel,
    QLabel#reportsInventoryAgeStatus,
    QLabel#reportsInventoryAgeContext,
    QLabel#reportsInventoryAgeEvidence,
    QLabel#reportsInventoryAgeGuardrails,
    QLabel#reportsInventoryTurnoverStatus,
    QLabel#reportsTurnoverPeriod,
    QLabel#reportsTurnoverFormula,
    QLabel#reportsTurnoverEvidence,
    QLabel#reportsTurnoverGuardrails {{
        color: {color(ColorRole.TEXT_SECONDARY)};
    }}

    QTableWidget#reportsCatalogTable,
    QTableWidget#reportsResultTable {{
        background: {color(ColorRole.SURFACE_PRIMARY)};
        alternate-background-color: {color(ColorRole.SURFACE_SECONDARY)};
        border: 1px solid {color(ColorRole.BORDER_STRONG)};
        border-radius: {radius['panel']}px;
        gridline-color: {color(ColorRole.BORDER_SUBTLE)};
        color: {color(ColorRole.TEXT_PRIMARY)};
        selection-background-color: {color(ColorRole.SURFACE_INTERACTIVE)};
    }}

    QFrame#reportsInventoryAgeEvidenceGate {{
        background: {color(ColorRole.SURFACE_SECONDARY)};
        border: 1px solid {color(ColorRole.BORDER_SUBTLE)};
        border-radius: {radius['panel']}px;
    }}

    QLabel#reportsInventoryAgeEvidenceGateTitle {{
        color: {color(ColorRole.TEXT_PRIMARY)};
        font-size: 12pt;
        font-weight: 700;
    }}

    QGroupBox#reportsInventoryAgePanel,
    QGroupBox#reportsInventoryTurnoverPanel {{
        background: {color(ColorRole.SURFACE_PRIMARY)};
        border: 1px solid {color(ColorRole.BORDER_STRONG)};
        border-radius: {radius['prominent']}px;
        color: {color(ColorRole.TEXT_PRIMARY)};
        margin-top: 12px;
        padding: 18px 12px 12px 12px;
        font-weight: 700;
    }}

    QFrame#reportsInventoryAgeDaysCard,
    QFrame#reportsInventoryAgeSourceDateCard,
    QFrame#reportsInventoryAgeEvidenceCard,
    QFrame#reportsTurnoverPercentageCard,
    QFrame#reportsTurnoverRatioCard,
    QFrame#reportsTurnoverOpeningUnitsCard,
    QFrame#reportsTurnoverClosingUnitsCard,
    QFrame#reportsTurnoverCompletedSalesCard,
    QFrame#reportsTurnoverAverageUnitsCard {{
        background: {color(ColorRole.SURFACE_SECONDARY)};
        border: 1px solid {color(ColorRole.BORDER_SUBTLE)};
        border-radius: {radius['control']}px;
    }}

    QLabel#reportsInventoryAgeDaysCaption,
    QLabel#reportsInventoryAgeSourceDateCaption,
    QLabel#reportsInventoryAgeEvidenceCaption,
    QLabel#reportsTurnoverPercentageCaption,
    QLabel#reportsTurnoverRatioCaption,
    QLabel#reportsTurnoverOpeningUnitsCaption,
    QLabel#reportsTurnoverClosingUnitsCaption,
    QLabel#reportsTurnoverCompletedSalesCaption,
    QLabel#reportsTurnoverAverageUnitsCaption {{
        color: {color(ColorRole.TEXT_MUTED)};
        font-size: 9pt;
        font-weight: 700;
        letter-spacing: 0.4px;
    }}

    QLabel#reportsInventoryAgeDays,
    QLabel#reportsInventoryAgeSourceDate,
    QLabel#reportsInventoryAgeEvidence,
    QLabel#reportsTurnoverPercentage,
    QLabel#reportsTurnoverRatio,
    QLabel#reportsTurnoverOpeningUnits,
    QLabel#reportsTurnoverClosingUnits,
    QLabel#reportsTurnoverCompletedSales,
    QLabel#reportsTurnoverAverageUnits {{
        color: {color(ColorRole.TEXT_PRIMARY)};
        font-size: 16pt;
        font-weight: 700;
    }}

    QWidget#reportsInventoryAgeQueryForm {{
        background: {color(ColorRole.SURFACE_PRIMARY)};
        border: 1px solid {color(ColorRole.BORDER_SUBTLE)};
        border-radius: {radius['panel']}px;
        padding: 12px;
    }}

    QGroupBox#reportsPurchaseSourcePanel {{
        background: {color(ColorRole.SURFACE_PRIMARY)};
        border: 1px solid {color(ColorRole.BORDER_STRONG)};
        border-radius: {radius['prominent']}px;
        color: {color(ColorRole.TEXT_PRIMARY)};
        margin-top: 12px;
        padding: 18px 12px 12px 12px;
        font-weight: 700;
    }}

    QLabel#reportsPurchaseSourceStatus {{
        color: {color(ColorRole.TEXT_SECONDARY)};
    }}

    QFrame#reportsPurchaseSourceEmptyState {{
        background: {color(ColorRole.SURFACE_PRIMARY)};
        border: 1px solid {color(ColorRole.BORDER_STRONG)};
        border-radius: {radius['panel']}px;
    }}

    QLabel#reportsPurchaseSourceEmptyStateTitle {{
        color: {color(ColorRole.TEXT_PRIMARY)};
        font-size: 12pt;
        font-weight: 700;
    }}

    QLabel#reportsPurchaseSourceEmptyStateDetail {{
        color: {color(ColorRole.TEXT_SECONDARY)};
    }}

    QTableWidget#reportsPurchaseSourceTable {{
        background: {color(ColorRole.SURFACE_PRIMARY)};
        alternate-background-color: {color(ColorRole.SURFACE_SECONDARY)};
        border: 1px solid {color(ColorRole.BORDER_SUBTLE)};
        border-radius: {radius['panel']}px;
        color: {color(ColorRole.TEXT_PRIMARY)};
        gridline-color: {color(ColorRole.BORDER_SUBTLE)};
    }}    """.strip()
