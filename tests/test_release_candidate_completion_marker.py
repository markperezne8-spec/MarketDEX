from pathlib import Path


def test_release_candidate_completion_marker_is_definition_only():
    text = (Path(__file__).resolve().parents[1] / "docs" / "RELEASE_CANDIDATE_COMPLETION_MARKER.md").read_text(encoding="utf-8")

    assert "checkpoint contract is explicit" in text
    assert "offline-first" in text
    assert "operator-authoritative" in text
    assert "Windows execution remains pending" in text
    assert "does not certify the packaged executable" in text
