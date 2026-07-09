from pathlib import Path


def test_release_candidate_checkpoint_pr_records_final_hardening_boundary():
    text = (Path(__file__).resolve().parents[1] / "docs" / "RELEASE_CANDIDATE_CHECKPOINT_PR.md").read_text(encoding="utf-8")

    assert "five permanent CI jobs" in text
    assert "Runtime operator data preservation is mandatory" in text
    assert "Inventory → Pricing → Listing → Sale History" in text
    assert "Windows launch, relaunch" in text
    assert "No marketplace polling, inferred sales, or remote mutation" in text
