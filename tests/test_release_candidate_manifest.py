from pathlib import Path


def test_release_candidate_manifest_records_checkpoint_artifacts_and_status():
    text = (Path(__file__).resolve().parents[1] / "docs" / "RELEASE_CANDIDATE_MANIFEST.md").read_text(encoding="utf-8")

    assert "Final release-candidate checkpoint definition" in text
    assert "RELEASE_CANDIDATE_CHECKPOINT.md" in text
    assert "RELEASE_CANDIDATE_VERIFICATION.md" in text
    assert "RELEASE_CANDIDATE_TEST_MATRIX.md" in text
    assert "tests/test_release_candidate_*.py" in text
    assert "exact Windows candidate execution pending" in text
