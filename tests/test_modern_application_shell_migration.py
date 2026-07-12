from __future__ import annotations

from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MAIN_WINDOW = REPOSITORY_ROOT / "ui" / "main_window.py"
APPLICATION_COMPOSITION = REPOSITORY_ROOT / "composition" / "application_composition.py"


def test_main_window_declares_one_branded_application_shell():
    source = MAIN_WINDOW.read_text(encoding="utf-8")

    assert "marketdexApplicationShell" in source
    assert "marketdexNavigationRail" in source
    assert "marketdexWorkspaceFrame" in source
    assert "marketdexStatusBar" in source
    assert "QStackedWidget" in source


def test_shell_exposes_persistent_workspace_navigation():
    source = MAIN_WINDOW.read_text(encoding="utf-8")

    for label in (
        "Mission Control",
        "Inventory",
        "Pricing",
        "Listing Workflow",
    ):
        assert repr(label) in source

    assert "setCurrentIndex" in source


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
