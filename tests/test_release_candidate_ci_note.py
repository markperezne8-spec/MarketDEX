from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_candidate_ci_note_matches_core_test_selection():
    note = (ROOT / "docs" / "RELEASE_CANDIDATE_CI_NOTE.md").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "Core Tests job explicitly selects that marker" in note
    assert "or release_candidate" in workflow
    assert "Windows operator checkpoint is a separate release verification action" in note
