from pathlib import Path


def test_build_progress_preserves_completed_listing_preparation_boundary():
    progress = Path('docs/BUILD_PROGRESS.md').read_text(encoding='utf-8')
    contract = Path('docs/MARKETPLACE_LISTING_PREPARATION_PROGRESS_CONTRACT.md').read_text(encoding='utf-8')
    assert '88%' in contract
    assert 'Marketplace Listing Preparation' in contract
    assert 'listing package review and completion tracking' in contract.lower()
    assert 'Marketplace Listing Preparation' in progress
    assert 'Marketplace Listing Package Review' in progress
