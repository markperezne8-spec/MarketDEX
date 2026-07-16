from __future__ import annotations

from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MAIN_WINDOW = REPOSITORY_ROOT / "ui" / "main_window.py"
WORKSPACE_HOST = REPOSITORY_ROOT / "ui" / "workspace_host.py"
WORKSPACE_CATALOG = REPOSITORY_ROOT / "ui" / "shell_workspace_catalog.py"
APPLICATION_COMPOSITION = REPOSITORY_ROOT / "composition" / "application_composition.py"


def test_main_window_declares_one_branded_application_shell():
    source = WORKSPACE_HOST.read_text(encoding="utf-8")

    assert "marketdexApplicationShell" in source
    assert "marketdexNavigationRail" in source
    assert "marketdexWorkspaceFrame" in source
    assert "marketdexStatusBar" in source
    assert "QStackedWidget" in source


def test_shell_exposes_persistent_workspace_navigation():
    source = WORKSPACE_HOST.read_text(encoding="utf-8")
    catalog = WORKSPACE_CATALOG.read_text(encoding="utf-8")

    for label in (
        "Inventory",
        "Pricing",
        "Listing Workflow",
    ):
        assert label in catalog

    assert "setCurrentIndex" in source

    mission_control = MAIN_WINDOW.read_text(encoding="utf-8")
    assert "Mission Control" in mission_control


def test_north_star_navigation_treatment_is_visual_only():
    source = WORKSPACE_HOST.read_text(encoding="utf-8")

    assert "m1.14d-north-star-left-navigation" in source
    assert "build_visual_north_star_tokens" in source
    assert "workspace-navigation" in source
    for prohibited in (
        "QTimer",
        "socket",
        "requests",
        "urllib",
        "sqlite3",
        "open(",
        "poll",
        "database",
        "persist",
        "save",
        "mutation",
        "import_inventory",
        "export_inventory",
        "add_asset",
        "adjust_asset",
        "archive_asset",
        "restore_asset",
    ):
        assert prohibited not in source


def test_shell_migration_preserves_existing_business_surfaces():
    source = MAIN_WINDOW.read_text(encoding="utf-8")

    for required in (
        "self.service.snapshot()",
        "self.refresh_inventory()",
        "self.inventory_service",
        "self.import_inventory",
        "self.export_inventory",
        "self.add_asset",
    ):
        assert required in source


def test_application_composition_still_builds_only_canonical_main_window():
    source = APPLICATION_COMPOSITION.read_text(encoding="utf-8")

    assert "window = MainWindow(self.mission_control, self.inventory)" in source
    assert "install_features(window)" in source
    assert "install_viewport_fit_feature(window, self.workspace_registry)" in source
    assert "ApplicationShell" not in source
