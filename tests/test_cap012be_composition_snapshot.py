from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_composition_builds_and_injects_purchase_source_snapshot() -> None:
    source = (ROOT / "composition" / "application_composition.py").read_text(encoding="utf-8")

    assert "PurchaseSourcePerformanceRequest" in source
    assert "present_purchase_source_performance" in source
    assert "_build_purchase_source_performance_presentation" in source
    assert "purchase_source_presentation=self.purchase_source_performance_presentation" in source


def test_reports_workspace_remains_presentation_only() -> None:
    source = (ROOT / "ui" / "reports_workspace.py").read_text(encoding="utf-8")

    assert "PurchaseSourcePerformancePresentation" in source
    assert "Sqlite" not in source
    assert "ApplicationComposition" not in source
    assert "INSERT" not in source
    assert "UPDATE" not in source
    assert "DELETE" not in source
