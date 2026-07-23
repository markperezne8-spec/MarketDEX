from __future__ import annotations

from app.engines.mission_control.data_freshness import DataFreshnessViewModel
from ui.data_freshness_panel import DataFreshnessPanel


def install_data_freshness_feature(
    window,
    view_model: DataFreshnessViewModel | None = None,
) -> DataFreshnessPanel:
    """Mount the read-only Data Freshness shell in Mission Control."""

    panel = DataFreshnessPanel(view_model=view_model, parent=window)
    window.data_freshness_panel = panel
    window.dashboard_grid.addWidget(panel, 6, 0, 1, 2)
    return panel
