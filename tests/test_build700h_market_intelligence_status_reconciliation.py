from pathlib import Path


FOUNDATION = Path('docs/Architecture/BUILD_700_MARKET_INTELLIGENCE_FOUNDATION.md')


def test_build_700_document_records_delivered_read_only_slice():
    text = FOUNDATION.read_text(encoding='utf-8')

    assert '**Status:** PARTIAL — offline read-only operator slice delivered' in text
    assert 'PR #186' in text
    assert 'PR #188' in text
    assert 'PR #192' in text
    assert 'PR #194' in text
    assert 'PR #196' in text
    assert 'Market Observation Gateway' in text
    assert 'Market Attention Signal service' in text
    assert 'Market Intelligence workspace' in text
    assert 'offline sample evidence visualization' in text


def test_build_700_document_preserves_unapproved_authority_boundaries():
    text = FOUNDATION.read_text(encoding='utf-8')

    assert 'No live provider is approved.' in text
    assert 'No persistent market-price authority is approved.' in text
    assert 'No automated execution authority is approved.' in text
    assert 'Product Registry, Inventory, Collection, Listing, Portfolio, Reports, or Settlement' in text
