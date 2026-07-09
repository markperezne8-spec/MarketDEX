from pathlib import Path


def test_rc_delivery_decision_boundary_assigns_authority():
    boundary = Path('docs/RC_DELIVERY_DECISION_BOUNDARY.md').read_text(encoding='utf-8')

    assert 'Build authority: `MarketDEX.spec` and `launcher.py`' in boundary
    assert 'Delivery authority: manually dispatched `Windows RC Delivery` workflow' in boundary
    assert 'Operator authority: download, extract outside the repository' in boundary
    assert 'does not install, update, publish marketplace listings, or alter cloud state' in boundary
