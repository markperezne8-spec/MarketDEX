import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication, QDialogButtonBox

from ui.inventory_listing_readiness_feature import ListingDraftDialog, edit_listing_draft


def test_listing_draft_dialog_exposes_save_control():
    app = QApplication.instance() or QApplication([])
    dialog = ListingDraftDialog(
        {
            'quantity': 2,
            'listing_status': 'Ready to List',
            'marketplace': 'eBay',
            'listing_title': 'Test Card',
            'listing_notes': 'Pack carefully',
            'asking_price_minor': 1500,
            'sku': 'TEST-001',
            'shipping_path': 'Standard Mail',
        }
    )

    save_button = dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.Save)

    assert callable(edit_listing_draft)
    assert save_button is not None
    assert save_button.isEnabled()
    dialog.close()
