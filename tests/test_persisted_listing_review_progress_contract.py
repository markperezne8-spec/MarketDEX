from pathlib import Path
import re


def test_build_progress_preserves_persisted_listing_review_boundary():
    progress = Path('docs/BUILD_PROGRESS.md').read_text(encoding='utf-8')
    contract = Path('docs/PERSISTED_LISTING_REVIEW_PROGRESS_CONTRACT.md').read_text(encoding='utf-8')
    progress_percent = int(re.search(r'Current engineering progress: \*\*(\d+)%\*\*', progress).group(1))
    assert progress_percent >= 92 and '92%' in contract
    assert 'Persisted Listing Review State' in progress
    assert 'completion marker' in contract.lower()
    assert 'Completed Listing Package Queue' in progress
