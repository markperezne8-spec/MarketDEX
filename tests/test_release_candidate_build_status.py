from pathlib import Path


def test_release_candidate_status_does_not_claim_unverified_windows_result():
    text = (Path(__file__).resolve().parents[1] / "docs" / "RELEASE_CANDIDATE_BUILD_STATUS.md").read_text(encoding="utf-8")

    assert "WINDOWS EXECUTION PENDING" in text
    assert "not yet declared verified" in text
    assert "packaged Windows checkpoint" in text
    assert "preserved operator runtime data" in text
