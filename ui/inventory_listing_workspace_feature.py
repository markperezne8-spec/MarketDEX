from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel


def listing_workspace_summary(asset_name, marketplace, target_price_minor, recommended_minor, net_profit_minor, roi_percent, readiness):
    variance = target_price_minor - recommended_minor
    position = 'ON RECOMMENDATION' if variance == 0 else ('ABOVE RECOMMENDATION' if variance > 0 else 'BELOW RECOMMENDATION')
    return f"LISTING DECISION • {asset_name} • {marketplace} • Target ${target_price_minor/100:,.2f} • {position} ${abs(variance)/100:,.2f} • Net ${net_profit_minor/100:,.2f} • ROI {roi_percent:.1f}% • {readiness}"


def install_inventory_listing_workspace_feature(window):
    box = QGroupBox('🧭 LISTING DECISION WORKSPACE')
    box_layout = QVBoxLayout(box)
    summary = QLabel('Select one inventory asset to build a listing decision.')
    summary.setWordWrap(True); summary.setStyleSheet('font-size:15px;font-weight:700')
    box_layout.addWidget(summary)
    window.inventory_listing_workspace = box; window.inventory_listing_workspace_summary = summary
    layout = window.inventory_panel.layout(); layout.insertWidget(layout.indexOf(window.refresh_button), box)

    def refresh_workspace():
        asset_id = window.selected_asset_id()
        if asset_id is None:
            summary.setText('Select one inventory asset to build a listing decision.'); return
        row = next(row for row in window.inventory_rows if row['asset_id'] == asset_id)
        qty = int(row['quantity']); unit_cost = 0 if qty <= 0 else round(int(row['total_cost_minor']) / qty)
        sale = round(window.inventory_target_sale_price.value() * 100)
        shipping = round(window.inventory_shipping_cost.value() * 100); packaging = round(window.inventory_packaging_cost.value() * 100)
        from ui.inventory_profit_feature import profit_decision
        from ui.inventory_price_guidance_feature import price_guidance
        from ui.inventory_sale_readiness_feature import sale_decision
        profit = profit_decision(unit_cost, sale, window.inventory_fee_percent.value(), shipping, packaging)
        guidance = price_guidance(unit_cost, window.inventory_fee_percent.value(), shipping, packaging, window.inventory_target_roi.value())
        readiness = sale_decision(row, sale)['status']
        summary.setText(listing_workspace_summary(row['asset_name'], window.inventory_marketplace.currentText(), sale, guidance['recommended_minor'], profit['net_profit_minor'], profit['roi_percent'], readiness))

    original_show = window.show_selected
    def show_selected(): original_show(); refresh_workspace()
    window.show_selected = show_selected; window.inventory_table.itemSelectionChanged.disconnect(); window.inventory_table.itemSelectionChanged.connect(window.show_selected)
    for signal in (window.inventory_target_sale_price.valueChanged, window.inventory_fee_percent.valueChanged, window.inventory_shipping_cost.valueChanged, window.inventory_packaging_cost.valueChanged, window.inventory_target_roi.valueChanged, window.inventory_marketplace.currentTextChanged): signal.connect(refresh_workspace)
    refresh_workspace()
