from math import ceil
from PySide6.QtWidgets import QLabel, QDoubleSpinBox, QPushButton, QHBoxLayout


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
    controls = QHBoxLayout()
    controls.addWidget(QLabel('Target ROI'))
    target_roi = QDoubleSpinBox(); target_roi.setRange(0, 1000); target_roi.setDecimals(1); target_roi.setSuffix('%'); target_roi.setValue(20.0)
    use_recommended = QPushButton('Use Recommended Price'); use_recommended.setEnabled(False)
    controls.addWidget(target_roi); controls.addWidget(use_recommended); controls.addStretch(1)
    label = QLabel('PRICE GUIDANCE: Select one inventory asset.'); label.setWordWrap(True)
    window.inventory_target_roi = target_roi; window.inventory_use_recommended_price = use_recommended; window.inventory_price_guidance = label
    layout = window.inventory_panel.layout(); anchor = layout.indexOf(window.refresh_button); layout.insertLayout(anchor, controls); layout.insertWidget(anchor + 1, label)
    state = {'recommended_minor': 0}

    def refresh_guidance():
        asset_id = window.selected_asset_id()
        if asset_id is None:
            state['recommended_minor'] = 0; use_recommended.setEnabled(False); label.setText('PRICE GUIDANCE: Select one inventory asset.'); return
        row = next(row for row in window.inventory_rows if row['asset_id'] == asset_id)
        qty = int(row['quantity']); unit_cost = 0 if qty <= 0 else round(int(row['total_cost_minor']) / qty)
        result = price_guidance(unit_cost, window.inventory_fee_percent.value(), round(window.inventory_shipping_cost.value() * 100), round(window.inventory_packaging_cost.value() * 100), target_roi.value())
        state['recommended_minor'] = result['recommended_minor']; use_recommended.setEnabled(result['recommended_minor'] > 0)
        label.setText(f"PRICE GUIDANCE: Break-even {window._money(result['break_even_minor'])} • Minimum Profit {window._money(result['minimum_profit_minor'])} • Recommended {target_roi.value():.1f}% ROI {window._money(result['recommended_minor'])}")

    def apply_recommended():
        window.inventory_target_sale_price.setValue(state['recommended_minor'] / 100)

    original_show = window.show_selected
    def show_selected(): original_show(); refresh_guidance()
    window.show_selected = show_selected; window.inventory_table.itemSelectionChanged.disconnect(); window.inventory_table.itemSelectionChanged.connect(window.show_selected)
    window.inventory_fee_percent.valueChanged.connect(refresh_guidance); window.inventory_shipping_cost.valueChanged.connect(refresh_guidance); window.inventory_packaging_cost.valueChanged.connect(refresh_guidance); target_roi.valueChanged.connect(refresh_guidance); use_recommended.clicked.connect(apply_recommended)
    refresh_guidance()
