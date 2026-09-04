import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication, QDialogButtonBox

from ui.inventory_listing_readiness_feature import ListingDraftDialog, MarketPriceHistoryDialog


APP = QApplication.instance() or QApplication([])


def test_listing_draft_market_pricing_section_shows_updated_state():
    dialog = ListingDraftDialog(
        {
            'quantity': 2,
            'listing_status': 'Ready to List',
            'marketplace': 'eBay',
            'listing_title': 'Pikachu',
            'listing_notes': 'Handle carefully',
            'asking_price_minor': 2500,
            'sku': 'SKU-1',
            'shipping_path': 'Standard Mail',
            'online_market_price_minor': 1234,
            'online_market_currency': 'USD',
            'online_market_price_status': 'UPDATED',
            'online_market_updated_at': '2026-09-03T12:00:00+00:00',
            'online_market_source_name': 'TCGplayer API',
        }
    )

    assert dialog.market_price_value.text() == 'USD $12.34'
    assert dialog.market_price_status.text() == 'Updated'
    assert dialog.market_price_source.text() == 'TCGplayer API'
    assert dialog.refresh_price_button.text() == 'Refresh Price'
    assert dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.Save) is not None
    dialog.close()
    dialog.deleteLater()
    APP.processEvents()


def test_listing_draft_market_pricing_section_shows_unavailable_state():
    dialog = ListingDraftDialog(
        {
            'quantity': 1,
            'listing_status': 'Ready to List',
            'online_market_price_status': 'CREDENTIALS_MISSING',
            'online_market_error_message': 'TCGPLAYER_BEARER_TOKEN is not configured.',
        }
    )

    assert dialog.market_price_value.text() == 'Price unavailable'
    assert 'TCGPLAYER_BEARER_TOKEN' in dialog.market_price_status.text()
    assert dialog.market_price_updated.text() == 'Never'
    dialog.close()
    dialog.deleteLater()
    APP.processEvents()


def test_market_price_history_dialog_renders_observations():
    dialog = MarketPriceHistoryDialog(
        [
            {
                'market_price_minor': 1234,
                'currency': 'USD',
                'price_status': 'UPDATED',
                'source_name': 'TCGplayer API',
                'observed_at': '2026-09-03T12:00:00+00:00',
                'match_reference': 'product-123',
                'error_message': '',
            },
            {
                'market_price_minor': None,
                'currency': 'USD',
                'price_status': 'NETWORK_ERROR',
                'source_name': 'TCGplayer API',
                'observed_at': '2026-09-03T13:00:00+00:00',
                'match_reference': '',
                'error_message': 'Offline',
            },
        ]
    )

    assert dialog.table.rowCount() == 2
    assert dialog.table.item(0, 1).text() == 'USD $12.34'
    assert dialog.table.item(0, 2).text() == 'Updated'
    assert dialog.table.item(1, 1).text() == 'Price unavailable'
    assert dialog.table.item(1, 5).text() == 'Offline'
    dialog.close()
    dialog.deleteLater()
    APP.processEvents()


def test_empty_market_price_history_keeps_headers_readable():
    dialog = MarketPriceHistoryDialog([])

    assert dialog.table.rowCount() == 0
    assert dialog.table.columnWidth(0) >= 160
    assert dialog.table.columnWidth(5) >= 220
    assert dialog.width() >= 1030
    assert dialog.table.horizontalHeaderItem(0).text() == 'Observed'
    assert dialog.table.horizontalHeaderItem(5).text() == 'Error'
    dialog.close()
    dialog.deleteLater()
    APP.processEvents()
