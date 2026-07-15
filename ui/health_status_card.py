from __future__ import annotations

from PySide6.QtWidgets import QLabel

from app.engines.health.status_view_model import (
    HealthStatusViewModel,
    build_health_status_view_model,
)
from ui.design_system.widgets import MarketDEXDashboardPanel


class HealthStatusCard(MarketDEXDashboardPanel):
    """Compact read-only Health status surface backed by injected evidence."""

    def __init__(self, view_model: HealthStatusViewModel | None = None, parent=None) -> None:
        super().__init__('System Health', 'Read-only Health readiness', parent)
        self.view_model = view_model or build_health_status_view_model(status_text=None)
        self.status_label = QLabel(self.view_model.status_text, self.content_widget)
        self.status_label.setObjectName('healthStatusText')
        self.status_label.setWordWrap(True)
        self.diagnostics_label = QLabel(self.content_widget)
        self.diagnostics_label.setObjectName('healthDiagnosticLines')
        self.diagnostics_label.setWordWrap(True)
        self.diagnostics_label.setText(
            '\n'.join(self.view_model.diagnostic_lines)
            if self.view_model.diagnostic_lines
            else 'No diagnostic details available.'
        )
        self.add_content_widget(self.status_label)
        self.add_content_widget(self.diagnostics_label)
        self.setAccessibleName(
            f'System Health. {self.view_model.status_text}. {self.diagnostics_label.text()}'
        )
