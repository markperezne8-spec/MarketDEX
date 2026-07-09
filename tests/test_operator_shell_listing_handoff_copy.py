from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_pricing_to_listing_handoff_is_operator_facing():
    assert 'Pricing work is complete here.' in SOURCE
    assert 'prepare, review, and record marketplace work' in SOURCE
    assert 'listing decisions, package review, operator handoff, LISTED outcomes' not in SOURCE
