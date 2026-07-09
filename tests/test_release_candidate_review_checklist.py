from pathlib import Path


def test_release_candidate_review_checklist_covers_checkpoint_review():
    text = (Path(__file__).resolve().parents[1] / "docs" / "RELEASE_CANDIDATE_REVIEW_CHECKLIST.md").read_text(encoding="utf-8")

    assert "Exactly five permanent CI jobs remain" in text
    assert "Core Tests execute `release_candidate` contract tests" in text
    assert "Inventory → Pricing → Listing context continuity" in text
    assert "No document claims the Windows checkpoint has already passed" in text
    assert "exact candidate execution, not feature expansion" in text
