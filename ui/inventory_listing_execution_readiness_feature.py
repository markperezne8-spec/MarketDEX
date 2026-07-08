from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel
from core.listing_plan_repository import ListingPlanRepository
from ui.inventory_sale_readiness_feature import sale_decision


def listing_execution_readiness(row, plan):
    checks = {
        'active_quantity': int(row['quantity']) > 0,
        'marketplace': bool(str(plan['marketplace']).strip()),
        'target_price': int(plan['target_sale_price_minor']) > 0,
        'sale_ready': sale_decision(row, int(plan['target_sale_price_minor']))['status'] == 'SALE READY',
    }
    missing = [name.replace('_', ' ').title() for name, passed in checks.items() if not passed]
    return {'ready': all(checks.values()), 'checks': checks, 'missing': missing}


def install_inventory_listing_execution_readiness_feature(window):
    repository = ListingPlanRepository(window.inventory_service.database)
    box = QGroupBox('🚦 LISTING EXECUTION READINESS')
    layout = QVBoxLayout(box)
    summary = QLabel('Select one inventory asset with a saved listing plan.')
    summary.setWordWrap(True)
    summary.setStyleSheet('font-size:15px;font-weight:700')
    checklist = QLabel('EXECUTION CHECKS: Waiting for saved plan.')
    checklist.setWordWrap(True)
    layout.addWidget(summary)
    layout.addWidget(checklist)
    panel_layout = window.inventory_panel.layout()
    panel_layout.insertWidget(panel_layout.indexOf(window.refresh_button), box)
    window.inventory_listing_execution_readiness = box
    window.inventory_listing_execution_readiness_summary = summary
    window.inventory_listing_execution_readiness_checklist = checklist

    def refresh_readiness():
        asset_id = window.selected_asset_id()
        if asset_id is None:
            summary.setText('Select one inventory asset with a saved listing plan.')
            checklist.setText('EXECUTION CHECKS: Waiting for saved plan.')
            return
        row = next(row for row in window.inventory_rows if row['asset_id'] == asset_id)
        plan = repository.get(asset_id)
        if plan is None:
            summary.setText(f"NOT READY • {row['asset_name']} • Save a listing plan first.")
            checklist.setText('EXECUTION CHECKS: Saved Plan missing.')
            return
        result = listing_execution_readiness(row, plan)
        labels = [('Quantity', result['checks']['active_quantity']), ('Marketplace', result['checks']['marketplace']), ('Target Price', result['checks']['target_price']), ('Sale Ready', result['checks']['sale_ready'])]
        checklist.setText('EXECUTION CHECKS: ' + ' • '.join(f"{'✓' if passed else '✗'} {label}" for label, passed in labels))
        summary.setText((f"READY TO PREPARE • {row['asset_name']} • {plan['marketplace']} • ${plan['target_sale_price_minor']/100:,.2f}") if result['ready'] else (f"NOT READY • {row['asset_name']} • Fix: {', '.join(result['missing'])}"))

    original_show = window.show_selected
    def show_selected():
        original_show()
        refresh_readiness()
    window.show_selected = show_selected
    window.inventory_table.itemSelectionChanged.disconnect()
    window.inventory_table.itemSelectionChanged.connect(window.show_selected)
    window.inventory_save_listing_plan.clicked.connect(refresh_readiness)
    window.refresh_listing_execution_readiness = refresh_readiness
    refresh_readiness()
