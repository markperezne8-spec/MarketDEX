from pathlib import Path


def test_listing_preparation_summary_contract_matches_ui():
    source = Path('ui/inventory_marketplace_listing_preparation_feature.py').read_text(encoding='utf-8')
    contract = Path('docs/MARKETPLACE_LISTING_PREPARATION_SUMMARY_CONTRACT.md').read_text(encoding='utf-8')
    for marker in ['LISTING PACKAGE READY', 'OFFLINE PREPARATION ONLY', 'PACKAGE BLOCKED']:
        assert marker in source
        assert marker in contract
    for label in ['MARKETPLACE', 'TITLE', 'QUANTITY', 'TARGET PRICE', 'ASSET ID']:
        assert label in source
        assert label in contract
