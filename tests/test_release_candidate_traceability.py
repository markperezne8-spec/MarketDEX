from pathlib import Path


def test_release_candidate_traceability_links_checkpoint_artifacts():
    text = (Path(__file__).resolve().parents[1] / "docs" / "RELEASE_CANDIDATE_TRACEABILITY.md").read_text(encoding="utf-8")

    for path in (
        "docs/BUILD_PROGRESS.md",
        "docs/RELEASE_CANDIDATE_CHECKPOINT.md",
        "docs/RELEASE_CANDIDATE_VERIFICATION.md",
        "docs/RELEASE_CANDIDATE_TEST_MATRIX.md",
        "docs/RELEASE_CANDIDATE_SCOPE.md",
        "docs/RELEASE_CANDIDATE_ACCEPTANCE.md",
        "docs/RELEASE_CANDIDATE_BUILD_STATUS.md",
        "docs/RELEASE_CANDIDATE_NEXT_BOUNDARY.md",
        "docs/RELEASE_CANDIDATE_OPERATOR_NOTE.md",
        "docs/RELEASE_CANDIDATE_COMPLETION_MARKER.md",
        "docs/RELEASE_CANDIDATE_CHECKPOINT_PR.md",
    ):
        assert path in text
