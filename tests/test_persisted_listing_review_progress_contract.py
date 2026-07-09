from pathlib import Path


def test_build_progress_matches_persisted_listing_review_boundary():
    progress = Path('docs/BUILD_PROGRESS.md').read_text(encoding='utf-8')
    contract = Path('docs/PERSISTED_LISTING_REVIEW_PROGRESS_CONTRACT.md').read_text(encoding='utf-8')
    assert '92%' in progress and '92%' in contract
    assert 'Persisted Listing Review State and Completion Tracking' in progress
    assert 'completion marker' in contract.lower()
    assert 'completed listing package queue and operator handoff workflow' in progress.lower()
