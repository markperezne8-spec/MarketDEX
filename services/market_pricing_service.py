from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4


PRICE_SOURCE_NAME = 'TCGplayer API'
TCGPLAYER_API_BASE = 'https://api.tcgplayer.com'
PRICE_STALE_AFTER = timedelta(hours=24)
PRICE_UPDATED = 'UPDATED'
PRICE_UNAVAILABLE = 'PRICE_UNAVAILABLE'
CREDENTIALS_MISSING = 'CREDENTIALS_MISSING'
NETWORK_ERROR = 'NETWORK_ERROR'
INVALID_MATCH = 'INVALID_MATCH'
PRICE_STATUSES = (
    PRICE_UPDATED,
    PRICE_UNAVAILABLE,
    CREDENTIALS_MISSING,
    NETWORK_ERROR,
    INVALID_MATCH,
)

_CONDITION_IDS = {
    'near mint': 1,
    'lightly played': 2,
    'moderately played': 3,
    'heavily played': 4,
    'damaged': 5,
}


@dataclass(frozen=True)
class MarketPriceResult:
    market_price_minor: int | None
    currency: str
    source_name: str
    source_url: str
    last_updated: str
    price_status: str
    error_message: str = ''
    match_reference: str = ''

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso_now() -> str:
    return _utc_now().isoformat()


def _normalize(value: object) -> str:
    return re.sub(r'[^a-z0-9]+', ' ', str(value or '').casefold()).strip()


def _value(payload: dict, *names, default=None):
    for name in names:
        if name in payload:
            return payload[name]
    folded = {str(key).casefold(): value for key, value in payload.items()}
    for name in names:
        if name.casefold() in folded:
            return folded[name.casefold()]
    return default


def _results(payload: dict) -> list[dict]:
    values = _value(payload, 'results', default=[])
    return [value for value in values if isinstance(value, dict)]


def _errors(payload: dict) -> str:
    values = _value(payload, 'errors', default=[])
    if isinstance(values, list):
        return '; '.join(str(value) for value in values if value)
    return str(values or '')


def _price_minor(value: object) -> int | None:
    if value is None or value == '':
        return None
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return None
    if amount < 0:
        return None
    return round(amount * 100)


class TCGplayerMarketPriceProvider:
    """Read-only official TCGplayer catalog and market-price client."""

    def __init__(self, token: str | None = None, opener=None):
        self.token = token if token is not None else os.environ.get('TCGPLAYER_BEARER_TOKEN', '')
        self.opener = opener or urlopen

    def _request_json(self, url: str) -> dict:
        request = Request(
            url,
            headers={
                'Accept': 'application/json',
                'Authorization': f'bearer {self.token}',
            },
        )
        response = self.opener(request, timeout=15)
        try:
            raw = response.read()
        finally:
            close = getattr(response, 'close', None)
            if close:
                close()
        return json.loads(raw.decode('utf-8') if isinstance(raw, bytes) else raw)

    def _result(
        self,
        *,
        market_price_minor: int | None,
        source_url: str,
        status: str,
        error_message: str = '',
        match_reference: str = '',
    ) -> MarketPriceResult:
        return MarketPriceResult(
            market_price_minor=market_price_minor,
            currency='USD',
            source_name=PRICE_SOURCE_NAME,
            source_url=source_url,
            last_updated=_iso_now(),
            price_status=status,
            error_message=error_message,
            match_reference=match_reference,
        )

    def fetch_price(self, detail: dict) -> MarketPriceResult:
        product_name = str(detail.get('product_name') or detail.get('asset_name') or '').strip()
        set_name = str(detail.get('set_name') or '').strip()
        catalog_url = f'{TCGPLAYER_API_BASE}/catalog/products?' + urlencode(
            {
                'productName': product_name,
                **({'groupName': set_name} if set_name else {}),
                'includeSkus': 'true',
                'limit': '20',
            }
        )

        if not self.token:
            return self._result(
                market_price_minor=None,
                source_url=catalog_url,
                status=CREDENTIALS_MISSING,
                error_message='TCGPLAYER_BEARER_TOKEN is not configured.',
            )
        if not product_name:
            return self._result(
                market_price_minor=None,
                source_url=catalog_url,
                status=INVALID_MATCH,
                error_message='Product name is required for a TCGplayer match.',
            )

        try:
            catalog_payload = self._request_json(catalog_url)
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            return self._result(
                market_price_minor=None,
                source_url=catalog_url,
                status=NETWORK_ERROR,
                error_message=f'TCGplayer catalog request failed: {exc}',
            )

        products = [
            product
            for product in _results(catalog_payload)
            if _normalize(_value(product, 'name', 'cleanName', default='')) == _normalize(product_name)
        ]
        if len(products) != 1:
            message = (
                f'No exact TCGplayer catalog match for {product_name!r}.'
                if not products
                else f'Multiple exact TCGplayer catalog matches for {product_name!r}.'
            )
            return self._result(
                market_price_minor=None,
                source_url=catalog_url,
                status=INVALID_MATCH,
                error_message=message,
            )

        product = products[0]
        product_id = _value(product, 'productId')
        if not product_id:
            return self._result(
                market_price_minor=None,
                source_url=catalog_url,
                status=INVALID_MATCH,
                error_message='TCGplayer catalog match did not include a product id.',
            )

        condition = _normalize(detail.get('item_condition', ''))
        skus = _value(product, 'skus', default=[])
        if condition and skus:
            condition_id = _CONDITION_IDS.get(condition)
            if condition_id is None:
                return self._result(
                    market_price_minor=None,
                    source_url=catalog_url,
                    status=INVALID_MATCH,
                    error_message=f'Unsupported condition for exact TCGplayer matching: {detail.get("item_condition")}.',
                    match_reference=str(product_id),
                )
            matching_skus = [
                sku
                for sku in skus
                if _value(sku, 'conditionId', default=None) == condition_id
            ]
            if len(matching_skus) != 1:
                return self._result(
                    market_price_minor=None,
                    source_url=catalog_url,
                    status=INVALID_MATCH,
                    error_message='TCGplayer did not return one condition-matched SKU.',
                    match_reference=str(product_id),
                )
            product_condition_id = _value(matching_skus[0], 'productConditionId')
            if not product_condition_id:
                return self._result(
                    market_price_minor=None,
                    source_url=catalog_url,
                    status=INVALID_MATCH,
                    error_message='Condition-matched TCGplayer SKU did not include a product condition id.',
                    match_reference=str(product_id),
                )
            price_url = f'{TCGPLAYER_API_BASE}/pricing/marketprices/{product_condition_id}'
            try:
                price_payload = self._request_json(price_url)
            except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
                return self._result(
                    market_price_minor=None,
                    source_url=price_url,
                    status=NETWORK_ERROR,
                    error_message=f'TCGplayer price request failed: {exc}',
                    match_reference=str(product_condition_id),
                )
            price_row = _results(price_payload)[0] if _results(price_payload) else {}
            price_minor = _price_minor(_value(price_row, 'price'))
            if price_minor is None:
                return self._result(
                    market_price_minor=None,
                    source_url=price_url,
                    status=PRICE_UNAVAILABLE,
                    error_message=_errors(price_payload) or 'TCGplayer returned no market price for the matched SKU.',
                    match_reference=str(product_condition_id),
                )
            return self._result(
                market_price_minor=price_minor,
                source_url=price_url,
                status=PRICE_UPDATED,
                match_reference=str(product_condition_id),
            )

        price_url = f'{TCGPLAYER_API_BASE}/pricing/product/{product_id}'
        try:
            price_payload = self._request_json(price_url)
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            return self._result(
                market_price_minor=None,
                source_url=price_url,
                status=NETWORK_ERROR,
                error_message=f'TCGplayer price request failed: {exc}',
                match_reference=str(product_id),
            )
        price_rows = _results(price_payload)
        prices = [_price_minor(_value(row, 'marketPrice')) for row in price_rows]
        prices = [price for price in prices if price is not None]
        if not prices:
            return self._result(
                market_price_minor=None,
                source_url=price_url,
                status=PRICE_UNAVAILABLE,
                error_message=_errors(price_payload) or 'TCGplayer returned no market price for the matched product.',
                match_reference=str(product_id),
            )
        return self._result(
            market_price_minor=prices[0],
            source_url=price_url,
            status=PRICE_UPDATED,
            match_reference=str(product_id),
        )


class MarketPricingService:
    def __init__(self, inventory_service, provider=None):
        self.inventory_service = inventory_service
        self.provider = provider or TCGplayerMarketPriceProvider()

    @staticmethod
    def is_stale(detail: dict, now: datetime | None = None) -> bool:
        updated_at = detail.get('online_market_updated_at')
        if not updated_at:
            return True
        try:
            parsed = datetime.fromisoformat(str(updated_at).replace('Z', '+00:00'))
        except ValueError:
            return True
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        current = now or _utc_now()
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        return current - parsed >= PRICE_STALE_AFTER

    def refresh_price(self, asset_id: str) -> dict:
        detail = self.inventory_service.get_asset_detail(asset_id)
        try:
            result = self.provider.fetch_price(detail)
        except Exception as exc:
            result = MarketPriceResult(
                market_price_minor=None,
                currency='USD',
                source_name=PRICE_SOURCE_NAME,
                source_url='',
                last_updated=_iso_now(),
                price_status=NETWORK_ERROR,
                error_message=f'Market pricing request failed: {exc}',
            )
        payload = result.as_dict()
        payload['online_market_price_minor'] = payload.pop('market_price_minor')
        return self.inventory_service.record_online_market_price(
            asset_id=asset_id,
            **payload,
            request_id=f'market-price-{asset_id}-{uuid4().hex}',
        )

    def refresh_stale_prices(self, asset_ids=None) -> list[dict]:
        rows = self.inventory_service.list_inventory(
            include_details=True,
            listing_status='Ready to List',
        )
        allowed = set(asset_ids) if asset_ids is not None else None
        current = _utc_now()
        refreshed = []
        for row in rows:
            if allowed is not None and row['asset_id'] not in allowed:
                continue
            if self.is_stale(row, current):
                refreshed.append(self.refresh_price(row['asset_id']))
        return refreshed
