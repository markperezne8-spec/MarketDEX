from math import ceil
from PySide6.QtWidgets import QLabel


def price_guidance(unit_cost_minor, fee_percent, shipping_minor, packaging_minor, target_roi_percent=20.0):
    rate = fee_percent / 100
    if rate >= 1:
        return {'break_even_minor': 0, 'minimum_profit_minor': 0, 'recommended_minor': 0}
    fixed = unit_cost_minor + shipping_minor + packaging_minor
    break_even = ceil(fixed / (1 - rate))
    minimum_profit = ceil((fixed + 1) / (1 - rate))
    target_profit = unit_cost_minor * target_roi_percent / 100
    recommended = ceil((fixed + target_profit) / (1 - rate))
    return {'break_even_minor': break_even, 'minimum_profit_minor': minimum_profit, 'recommended_minor': recommended}


def install_inventory_price_guidance_feature(window):
    label = QLabel('PRICE GUIDANCE: Select one inventory asset.')
    label.setWordWrap(True)
    window.inventory_price_guidance = label
    layout = window.inventory_panel.layout()
    layout.insertWidget(layout.indexOf(window.refresh_button), label)

    def refresh_guidance():
        asset_id = window.selected_asset_id()
        if asset_id is None:
            label.setText('PRICE GUIDANCE: Select one inventory asset.')
            return
        row = next(row for row in window.inventory_rows if row['asset_id'] == asset_id)
        qty = int(row['quantity'])
        unit_cost = 0 if qty <= 0 else round(int(row['total_cost_minor']) / qty)
        result = price_guidance(unit_cost, window.inventory_fee_percent.value(), round(window.inventory_shipping_cost.value() * 100), round(window.inventory_packaging_cost.value() * 100))
        label.setText(f"PRICE GUIDANCE: Break-even {window._money(result['break_even_minor'])} • Minimum Profit {window._money(result['minimum_profit_minor'])} • Recommended 20% ROI {window._money(result['recommended_minor'])}")

    original_show = window.show_selected
    def show_selected():
        original_show()
        refresh_guidance()
    window.show_selected = show_selected
    window.inventory_table.itemSelectionChanged.disconnect()
    window.inventory_table.itemSelectionChanged.connect(window.show_selected)
    window.inventory_fee_percent.valueChanged.connect(refresh_guidance)
    window.inventory_shipping_cost.valueChanged.connect(refresh_guidance)
    window.inventory_packaging_cost.valueChanged.connect(refresh_guidance)
    refresh_guidance()
