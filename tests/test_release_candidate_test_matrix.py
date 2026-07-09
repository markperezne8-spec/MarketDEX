from pathlib import Path


def test_release_candidate_matrix_covers_required_desktop_boundaries():
    text = (Path(__file__).resolve().parents[1] / "docs" / "RELEASE_CANDIDATE_TEST_MATRIX.md").read_text(encoding="utf-8")

    for boundary in ("Permanent CI surface", "Startup", "Runtime data", "Inventory handoff", "Pricing handoff", "Listing handoff", "Listing planning", "Marketplace authority", "Sale authority"):
        assert boundary in text
    assert "Windows checkpoint failure blocks release-candidate verification" in text
    assert "No unrelated feature expansion" in text
