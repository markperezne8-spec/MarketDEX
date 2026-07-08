from pathlib import Path


def test_listing_preparation_feature_has_no_network_clients():
    source = Path('ui/inventory_marketplace_listing_preparation_feature.py').read_text(encoding='utf-8').lower()
    for token in ['requests.', 'httpx.', 'urllib.request', 'socket.', 'ebay api', 'tcgplayer api']:
        assert token not in source


def test_no_remote_side_effects_contract_is_explicit():
    source = Path('docs/MARKETPLACE_LISTING_PREPARATION_NO_REMOTE_SIDE_EFFECTS.md').read_text(encoding='utf-8')
    assert 'local calculation and UI rendering only' in source
    assert 'does not send network publication requests' in source
