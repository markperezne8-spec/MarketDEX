import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication, QDialogButtonBox

from ui.inventory_listing_readiness_feature import ListingDraftDialog


def test_listing_draft_market_pricing_section_shows_updated_state():
    app = QApplication.instance() or QApplication([])
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


def test_listing_draft_market_pricing_section_shows_unavailable_state():
    app = QApplication.instance() or QApplication([])
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
