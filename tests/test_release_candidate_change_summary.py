from pathlib import Path


def test_release_candidate_change_summary_states_checkpoint_value_and_pending_execution():
    text = (Path(__file__).resolve().parents[1] / "docs" / "RELEASE_CANDIDATE_CHANGE_SUMMARY.md").read_text(encoding="utf-8")

    assert "does not add a new business feature" in text
    assert "all five permanent CI jobs must pass" in text
    assert "Inventory → Pricing → Listing selection context" in text
    assert "operator-controlled" in text
    assert "Windows execution is still pending" in text
