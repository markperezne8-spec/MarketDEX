from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_reports_workspace_exposes_north_star_visual_contract_hooks() -> None:
    source = (ROOT / "ui" / "reports_workspace.py").read_text(encoding="utf-8")

    for object_name in (
        "reportsWorkspace",
        "reportsScrollContent",
        "reportsCatalogTable",
        "reportsInventoryTurnoverPanel",
        "reportsInventoryAgeQueryForm",
    ):
        assert f"setObjectName('{object_name}')" in source


def test_reports_qss_has_reports_surface_hierarchy_and_tokenized_panels() -> None:
    source = (ROOT / "ui" / "design_system" / "qt_theme.py").read_text(encoding="utf-8")

    for selector in (
        "QWidget#reportsWorkspace",
        "QWidget#reportsScrollContent",
        "QTableWidget#reportsCatalogTable",
        "QGroupBox#reportsInventoryTurnoverPanel",
        "QWidget#reportsInventoryAgeQueryForm",
        "QFrame#reportsTurnoverPercentageCard",
    ):
        assert selector in source
    assert "ColorRole.APP_BACKGROUND" in source
    assert "ColorRole.SURFACE_PRIMARY" in source
    assert "ColorRole.BORDER_STRONG" in source


def test_reports_visual_slice_does_not_add_execution_or_mutation_authority() -> None:
    source = (ROOT / "ui" / "reports_workspace.py").read_text(encoding="utf-8")
    assert "INSERT" not in source
    assert "UPDATE" not in source
    assert "DELETE" not in source
