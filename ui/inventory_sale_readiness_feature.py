from PySide6.QtWidgets import QLabel, QDoubleSpinBox, QHBoxLayout


def sale_decision(row, asking_price_minor):
    cost = int(row['total_cost_minor'])
    quantity = int(row['quantity'])
    unit_cost = 0 if quantity <= 0 else round(cost / quantity)
    margin_minor = int(asking_price_minor) - unit_cost
    margin_percent = 0.0 if asking_price_minor <= 0 else (margin_minor / asking_price_minor) * 100
    if asking_price_minor <= 0:
        status = 'SET ASKING PRICE'
    elif margin_minor < 0:
        status = 'LOSS'
    elif margin_percent < 15:
        status = 'THIN MARGIN'
    else:
        status = 'SALE READY'
    return {'unit_cost_minor': unit_cost, 'margin_minor': margin_minor, 'margin_percent': margin_percent, 'status': status}


def install_inventory_sale_readiness_feature(window):
    bar = QHBoxLayout()
    bar.addWidget(QLabel('Target Sale Price'))
    asking = QDoubleSpinBox()
    asking.setRange(0, 1000000)
    asking.setDecimals(2)
    asking.setPrefix('$')
    window.inventory_target_sale_price = asking
    bar.addWidget(asking)
    decision = QLabel('SALE READINESS: Select one inventory asset.')
    decision.setWordWrap(True)
    window.inventory_sale_readiness = decision
    bar.addWidget(decision, 1)
    panel_layout = window.inventory_panel.layout()
    panel_layout.insertLayout(panel_layout.indexOf(window.refresh_button), bar)

    original_show_selected = window.show_selected

    def refresh_decision():
        asset_id = window.selected_asset_id()
        if asset_id is None:
            decision.setText('SALE READINESS: Select one inventory asset.')
            return
        selected = next(row for row in window.inventory_rows if row['asset_id'] == asset_id)
        result = sale_decision(selected, round(asking.value() * 100))
        decision.setText(f"SALE READINESS: {result['status']} • Unit Cost {window._money(result['unit_cost_minor'])} • Projected Margin {window._money(result['margin_minor'])} • {result['margin_percent']:.1f}%")

    def show_selected():
        original_show_selected()
        refresh_decision()

    window.show_selected = show_selected
    window.inventory_table.itemSelectionChanged.disconnect()
    window.inventory_table.itemSelectionChanged.connect(window.show_selected)
    asking.valueChanged.connect(refresh_decision)
    window.show_selected()
