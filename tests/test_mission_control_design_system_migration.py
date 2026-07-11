from __future__ import annotations

from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MAIN_WINDOW = REPOSITORY_ROOT / "ui" / "main_window.py"

CANONICAL_SNAPSHOT_KEYS = {
    "inventory_units",
    "inventory_asset_count",
    "inventory_cost_minor",
    "completed_sales",
    "revenue_minor",
    "profit_minor",
    "verified_audits",
    "authority_events",
}


def test_mission_control_migration_uses_shared_header_and_kpi_components():
    source = MAIN_WINDOW.read_text(encoding="utf-8")

    assert "MarketDEXWorkspaceHeader" in source
    assert "MarketDEXKpiCard" in source
    assert "build_marketdex_qss" in source
    assert "build_visual_north_star_tokens" in source
    assert "QGroupBox(label)" not in source


def test_mission_control_migration_preserves_every_snapshot_key():
    source = MAIN_WINDOW.read_text(encoding="utf-8")

    for key in CANONICAL_SNAPSHOT_KEYS:
        assert repr(key) in source

    assert "snapshot=self.service.snapshot()" in source
    assert "self.refresh_inventory()" in source
    assert "snapshot['database_path']" in source


def test_mission_control_migration_does_not_expand_into_inventory_summary_cards():
    source = MAIN_WINDOW.read_text(encoding="utf-8")

    # FDN-002 is deliberately limited to the workspace header and the eight
    # Mission Control KPI cards. Inventory summary presentation remains unchanged.
    assert "for label,key in (('Assets','asset_count'),('Units','total_units'),('Filtered Cost','total_cost_minor'))" in source
    assert "box=QGroupBox(label)" in source
