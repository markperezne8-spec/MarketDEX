from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_reports_workspace_wires_purchase_source_presentation_preview() -> None:
    source = (ROOT / "ui" / "reports_workspace.py").read_text(encoding="utf-8")

    assert "PurchaseSourcePerformancePresentation" in source
    assert "purchase_source_presentation" in source
    assert "reportsPurchaseSourcePanel" in source
    assert "reportsPurchaseSourceTable" in source
    assert "_refresh_purchase_source_preview" in source


def test_purchase_source_preview_preserves_read_only_boundary() -> None:
    source = (ROOT / "ui" / "reports_workspace.py").read_text(encoding="utf-8")

    assert "query_report" in source
    assert "INSERT" not in source
    assert "UPDATE" not in source
    assert "DELETE" not in source
    assert "Review Result" in source
