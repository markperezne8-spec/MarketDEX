from pathlib import Path


def test_build_progress_matches_listing_preparation_progress_contract():
    progress = Path('docs/BUILD_PROGRESS.md').read_text(encoding='utf-8')
    contract = Path('docs/MARKETPLACE_LISTING_PREPARATION_PROGRESS_CONTRACT.md').read_text(encoding='utf-8')
    assert '88%' in progress and '88%' in contract
    assert 'Marketplace Listing Preparation' in progress and 'Marketplace Listing Preparation' in contract
    assert 'listing package review and completion tracking' in progress.lower()
    assert 'listing package review and completion tracking' in contract.lower()
