from pathlib import Path


def test_release_candidate_operator_note_requires_exact_candidate_build():
    text = (Path(__file__).resolve().parents[1] / "docs" / "RELEASE_CANDIDATE_OPERATOR_NOTE.md").read_text(encoding="utf-8")

    assert "intentionally deferred" in text
    assert "Do not use an older executable" in text
    assert "exact candidate commit" in text
    assert "five permanent CI gates are green" in text
