from pathlib import Path


def test_release_candidate_scope_remains_offline_first_and_operator_authoritative():
    text = (Path(__file__).resolve().parents[1] / "docs" / "RELEASE_CANDIDATE_SCOPE.md").read_text(encoding="utf-8")

    assert "offline-first Windows desktop regression" in text
    assert "runtime operator-data preservation" in text
    assert "Inventory → Pricing → Listing context continuity" in text
    assert "operator-authoritative listing and sale outcomes" in text
    for excluded in ("marketplace polling", "remote listing creation", "inferred sales", "automatic SOLD conversion", "cloud-required runtime behavior"):
        assert excluded in text
