from pathlib import Path


def test_release_candidate_acceptance_covers_final_checkpoint_contract():
    text = (Path(__file__).resolve().parents[1] / "docs" / "RELEASE_CANDIDATE_ACCEPTANCE.md").read_text(encoding="utf-8")

    assert "all five permanent CI gates" in text
    assert "complete operator chain" in text
    assert "non-empty runtime data preservation is mandatory" in text
    assert "Windows launch and relaunch checkpoint" in text
    assert "Inventory → Pricing → Listing selection continuity" in text
    assert "planning remains separate from sale completion" in text
    assert "does not claim a Windows verification result" in text
