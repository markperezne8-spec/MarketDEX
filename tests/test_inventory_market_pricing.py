import os
import sqlite3
from datetime import datetime, timedelta, timezone
from urllib.error import URLError

import pytest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from services.inventory_app_service import InventoryAppService
from services.market_pricing_service import (
    CREDENTIALS_MISSING,
    INVALID_MATCH,
    NETWORK_ERROR,
    PRICE_UNAVAILABLE,
    PRICE_UPDATED,
    MarketPriceResult,
    MarketPricingService,
    TCGplayerMarketPriceProvider,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        import json
        return json.dumps(self.payload).encode('utf-8')

    def close(self):
        return None


class QueueOpener:
    def __init__(self, responses):
        self.responses = list(responses)
        self.urls = []

    def __call__(self, request, timeout):
        self.urls.append(request.full_url)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return FakeResponse(response)


def detail(**overrides):
    value = {
        'asset_name': 'Pikachu',
        'product_name': 'Pikachu',
        'set_name': 'Base Set',
        'asset_type': 'SINGLE',
        'item_condition': 'Near Mint',
    }
    value.update(overrides)
    return value


def test_tcgplayer_provider_returns_condition_matched_market_price():
    opener = QueueOpener(
        [
            {
                'success': True,
                'results': [
                    {
                        'productId': 123,
                        'name': 'Pikachu',
                        'skus': [{'conditionId': 1, 'productConditionId': 456}],
                    }
                ],
            },
            {'success': True, 'results': [{'productConditionId': 456, 'price': 12.34}]},
        ]
    )

    result = TCGplayerMarketPriceProvider(token='test-token', opener=opener).fetch_price(detail())

    assert result.price_status == PRICE_UPDATED
    assert result.market_price_minor == 1234
    assert result.currency == 'USD'
    assert result.source_name == 'TCGplayer API'
    assert opener.urls[-1].endswith('/pricing/marketprices/456')


def test_stale_price_refresh_persists_without_changing_asking_price(tmp_path):
    inventory = InventoryAppService(tmp_path / 'marketdex.sqlite3')
    inventory.add_asset(
        asset_id='asset-1',
        asset_name='Pikachu',
        asset_type='SINGLE',
        quantity=2,
        total_cost_minor=500,
        request_id='add-1',
    )
    inventory.update_tcg_details(
        asset_id='asset-1',
        product_name='Pikachu',
        set_name='Base Set',
        item_condition='Near Mint',
        market_price_minor=1200,
        request_id='tcg-1',
    )
    inventory.update_listing_details(
        asset_id='asset-1',
        listing_status='Ready to List',
        marketplace='TCGplayer',
        asking_price_minor=2500,
        sku='SKU-1',
        storage_location='Binder A',
        listing_title='Pikachu',
        listing_notes='',
        photos_ready='Ready',
        shipping_path='Standard Mail',
        request_id='listing-1',
    )
    inventory.record_online_market_price(
        asset_id='asset-1',
        online_market_price_minor=1800,
        currency='USD',
        source_name='TCGplayer API',
        source_url='https://api.tcgplayer.com/pricing/product/123',
        last_updated=(datetime.now(timezone.utc) - timedelta(hours=25)).isoformat(),
        price_status=PRICE_UPDATED,
        request_id='price-old',
    )

    class StubProvider:
        def fetch_price(self, _detail):
            return MarketPriceResult(
                market_price_minor=3100,
                currency='USD',
                source_name='Mock TCGplayer API',
                source_url='https://example.test/price',
                last_updated=datetime.now(timezone.utc).isoformat(),
                price_status=PRICE_UPDATED,
            )

    service = MarketPricingService(inventory, StubProvider())
    assert service.is_stale(inventory.get_asset_detail('asset-1'))
    refreshed = service.refresh_stale_prices()

    assert len(refreshed) == 1
    reopened = InventoryAppService(tmp_path / 'marketdex.sqlite3')
    saved = reopened.get_asset_detail('asset-1')
    assert saved['online_market_price_minor'] == 3100
    assert saved['online_market_price_status'] == PRICE_UPDATED
    assert saved['asking_price_minor'] == 2500
    history = reopened.list_market_price_history('asset-1')
    assert len(history) == 2
    assert history[0]['market_price_minor'] == 3100
    assert history[0]['source_name'] == 'Mock TCGplayer API'
    assert history[1]['market_price_minor'] == 1800


def test_missing_credentials_is_explicit_and_does_not_call_network():
    opener = QueueOpener([])
    result = TCGplayerMarketPriceProvider(token='', opener=opener).fetch_price(detail())

    assert result.price_status == CREDENTIALS_MISSING
    assert 'TCGPLAYER_BEARER_TOKEN' in result.error_message
    assert opener.urls == []


def test_network_failure_is_saved_as_non_fatal_status():
    result = TCGplayerMarketPriceProvider(
        token='test-token',
        opener=QueueOpener([URLError('offline')]),
    ).fetch_price(detail())

    assert result.price_status == NETWORK_ERROR
    assert 'offline' in result.error_message


def test_invalid_product_match_is_not_priced():
    result = TCGplayerMarketPriceProvider(
        token='test-token',
        opener=QueueOpener([{'success': True, 'results': []}]),
    ).fetch_price(detail())

    assert result.price_status == INVALID_MATCH
    assert 'exact TCGplayer catalog match' in result.error_message


def test_unavailable_product_price_is_distinguished_from_invalid_match():
    result = TCGplayerMarketPriceProvider(
        token='test-token',
        opener=QueueOpener(
            [
                {'success': True, 'results': [{'productId': 123, 'name': 'Pikachu'}]},
                {'success': True, 'errors': ['No market price'], 'results': [{'marketPrice': None}]},
            ]
        ),
    ).fetch_price(detail(item_condition=''))

    assert result.price_status == PRICE_UNAVAILABLE
    assert 'No market price' in result.error_message


def test_market_price_history_retains_unavailable_status_and_error(tmp_path):
    inventory = InventoryAppService(tmp_path / 'marketdex.sqlite3')
    inventory.add_asset(
        asset_id='asset-2',
        asset_name='Mew',
        asset_type='SINGLE',
        quantity=1,
        total_cost_minor=100,
        request_id='add-2',
    )
    inventory.record_online_market_price(
        asset_id='asset-2',
        online_market_price_minor=None,
        currency='USD',
        source_name='TCGplayer API',
        source_url='https://api.tcgplayer.com/catalog/products',
        last_updated='2026-09-03T12:00:00+00:00',
        price_status=NETWORK_ERROR,
        error_message='Offline',
        request_id='price-error',
    )

    reopened = InventoryAppService(tmp_path / 'marketdex.sqlite3')
    history = reopened.list_market_price_history('asset-2')

    assert history == [{
        'observation_id': history[0]['observation_id'],
        'asset_id': 'asset-2',
        'market_price_minor': None,
        'currency': 'USD',
        'source_name': 'TCGplayer API',
        'source_url': 'https://api.tcgplayer.com/catalog/products',
        'observed_at': '2026-09-03T12:00:00+00:00',
        'price_status': NETWORK_ERROR,
        'error_message': 'Offline',
        'match_reference': '',
    }]
    assert reopened.get_asset_detail('asset-2')['asking_price_minor'] == 0
    with pytest.raises(sqlite3.IntegrityError, match='append-only'):
        with reopened.database.transaction() as connection:
            connection.execute(
                'DELETE FROM inventory_market_price_observations WHERE asset_id=?',
                ('asset-2',),
            )
