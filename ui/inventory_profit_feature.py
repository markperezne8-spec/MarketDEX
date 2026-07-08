from PySide6.QtWidgets import QLabel, QDoubleSpinBox, QComboBox, QGridLayout

MARKETPLACE_FEES = {'CUSTOM': 0.0, 'EBAY': 13.25, 'TCGPLAYER': 12.75}


def profit_decision(unit_cost_minor, sale_price_minor, fee_percent, shipping_minor, packaging_minor):
    fees = round(sale_price_minor * fee_percent / 100)
    net = sale_price_minor - fees - shipping_minor - packaging_minor - unit_cost_minor
    roi = 0.0 if unit_cost_minor <= 0 else net / unit_cost_minor * 100
    return {'fees_minor': fees, 'net_profit_minor': net, 'roi_percent': roi}


def install_inventory_profit_feature(window):
    grid = QGridLayout(); grid.addWidget(QLabel('Marketplace'), 0, 0)
    market = QComboBox(); market.addItems(MARKETPLACE_FEES); grid.addWidget(market, 0, 1)
    fee = QDoubleSpinBox(); fee.setRange(0, 100); fee.setDecimals(2); fee.setSuffix('%'); grid.addWidget(QLabel('Fee'), 0, 2); grid.addWidget(fee, 0, 3)
    shipping = QDoubleSpinBox(); shipping.setRange(0, 100000); shipping.setDecimals(2); shipping.setPrefix('$'); grid.addWidget(QLabel('Shipping'), 1, 0); grid.addWidget(shipping, 1, 1)
    packaging = QDoubleSpinBox(); packaging.setRange(0, 100000); packaging.setDecimals(2); packaging.setPrefix('$'); grid.addWidget(QLabel('Packaging'), 1, 2); grid.addWidget(packaging, 1, 3)
    result = QLabel('TRUE PROFIT: Select one inventory asset.'); result.setWordWrap(True); grid.addWidget(result, 2, 0, 1, 4)
    window.inventory_marketplace=market; window.inventory_fee_percent=fee; window.inventory_shipping_cost=shipping; window.inventory_packaging_cost=packaging; window.inventory_true_profit=result
    layout=window.inventory_panel.layout(); layout.insertLayout(layout.indexOf(window.refresh_button), grid)

    def refresh_profit():
        asset_id=window.selected_asset_id()
        if asset_id is None: result.setText('TRUE PROFIT: Select one inventory asset.'); return
        row=next(row for row in window.inventory_rows if row['asset_id']==asset_id)
        qty=int(row['quantity']); unit_cost=0 if qty<=0 else round(int(row['total_cost_minor'])/qty)
        sale=round(window.inventory_target_sale_price.value()*100)
        calc=profit_decision(unit_cost,sale,fee.value(),round(shipping.value()*100),round(packaging.value()*100))
        result.setText(f"TRUE PROFIT: {window._money(calc['net_profit_minor'])} • ROI {calc['roi_percent']:.1f}% • Fees {window._money(calc['fees_minor'])} • Shipping {window._money(round(shipping.value()*100))} • Packaging {window._money(round(packaging.value()*100))}")

    def marketplace_changed(name): fee.setValue(MARKETPLACE_FEES[name]); refresh_profit()
    original_show=window.show_selected
    def show_selected(): original_show(); refresh_profit()
    window.show_selected=show_selected; window.inventory_table.itemSelectionChanged.disconnect(); window.inventory_table.itemSelectionChanged.connect(window.show_selected)
    market.currentTextChanged.connect(marketplace_changed); fee.valueChanged.connect(refresh_profit); shipping.valueChanged.connect(refresh_profit); packaging.valueChanged.connect(refresh_profit); window.inventory_target_sale_price.valueChanged.connect(refresh_profit)
    marketplace_changed(market.currentText())
