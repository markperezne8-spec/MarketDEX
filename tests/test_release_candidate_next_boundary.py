from pathlib import Path


def test_release_candidate_next_boundary_requires_real_windows_checkpoint():
    text = (Path(__file__).resolve().parents[1] / "docs" / "RELEASE_CANDIDATE_NEXT_BOUNDARY.md").read_text(encoding="utf-8")

    assert "packaged MarketDEX executable" in text
    assert "preserved operator runtime data" in text
    assert "Repair only defects found by that checkpoint" in text
    assert "five permanent CI gates are green" in text
    assert "verified release-candidate checkpoint" in text
