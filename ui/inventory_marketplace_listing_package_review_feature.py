from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from core.listing_plan_repository import ListingPlanRepository
from core.listing_package_review_repository import ListingPackageReviewRepository
from ui.inventory_marketplace_listing_preparation_feature import marketplace_listing_package


def listing_package_review_decision(row, plan):
    package = marketplace_listing_package(row, plan)
    if not package['prepared']:
        return {'reviewable': False, 'status': 'REVIEW BLOCKED', 'reason': package['reason']}
    return {'reviewable': True, 'status': 'READY FOR OPERATOR REVIEW', 'reason': ''}


def install_inventory_marketplace_listing_package_review_feature(window):
    repository = ListingPlanRepository(window.inventory_service.database)
    review_repository = ListingPackageReviewRepository(window.inventory_service.database)
    box = QGroupBox('🔎 MARKETPLACE LISTING PACKAGE REVIEW')
    layout = QVBoxLayout(box)
    summary = QLabel('Select a prepared listing package for operator review.')
    summary.setWordWrap(True)
    summary.setStyleSheet('font-size:15px;font-weight:700')
    status = QLabel('REVIEW STATUS: Waiting for a prepared package.')
    status.setWordWrap(True)
    completion = QLabel('COMPLETION: Not complete')
    actions = QHBoxLayout()
    approve = QPushButton('Approve Package')
    reject = QPushButton('Return for Changes')
    approve.setEnabled(False)
    reject.setEnabled(False)
    actions.addWidget(approve)
    actions.addWidget(reject)
    layout.addWidget(summary)
    layout.addWidget(status)
    layout.addWidget(completion)
    layout.addLayout(actions)
    panel_layout = window.inventory_panel.layout()
    panel_layout.insertWidget(panel_layout.indexOf(window.refresh_button), box)
    window.inventory_marketplace_listing_package_review = box
    window.inventory_marketplace_listing_package_review_summary = summary
    window.inventory_marketplace_listing_package_review_status = status
    window.inventory_marketplace_listing_package_review_completion = completion
    window.inventory_approve_listing_package = approve
    window.inventory_return_listing_package = reject

    def refresh_review():
        asset_id = window.selected_asset_id()
        if asset_id is None:
            summary.setText('Select a prepared listing package for operator review.')
            status.setText('REVIEW STATUS: Waiting for a prepared package.')
            completion.setText('COMPLETION: Not complete')
            approve.setEnabled(False)
            reject.setEnabled(False)
            return
        row = next(row for row in window.inventory_rows if row['asset_id'] == asset_id)
        plan = repository.get(asset_id)
        if plan is None:
            summary.setText(f"REVIEW BLOCKED • {row['asset_name']} • Save a listing plan first.")
            status.setText('REVIEW STATUS: Package not reviewable.')
            completion.setText('COMPLETION: Not complete')
            approve.setEnabled(False)
            reject.setEnabled(False)
            return
        decision = listing_package_review_decision(row, plan)
        if not decision['reviewable']:
            summary.setText(f"REVIEW BLOCKED • {row['asset_name']} • Fix: {decision['reason']}")
            status.setText('REVIEW STATUS: Package not reviewable.')
            completion.setText('COMPLETION: Not complete')
            approve.setEnabled(False)
            reject.setEnabled(False)
            return
        summary.setText(f"READY FOR OPERATOR REVIEW • {row['asset_name']} • {plan['marketplace']} • ${plan['target_sale_price_minor']/100:,.2f}")
        persisted = review_repository.get(asset_id)
        current = persisted['review_state'] if persisted else 'PENDING OPERATOR DECISION'
        status.setText(f'REVIEW STATUS: {current}')
        completion.setText('COMPLETION: COMPLETE' if persisted and persisted['completed'] else 'COMPLETION: Not complete')
        approve.setEnabled(True)
        reject.setEnabled(True)

    def set_review_state(value):
        asset_id = window.selected_asset_id()
        if asset_id is None:
            return
        review_repository.save(asset_id, value)
        refresh_review()

    approve.clicked.connect(lambda: set_review_state('PACKAGE APPROVED • OFFLINE ONLY'))
    reject.clicked.connect(lambda: set_review_state('RETURNED FOR CHANGES'))
    original_show = window.show_selected

    def show_selected():
        original_show()
        refresh_review()

    window.show_selected = show_selected
    window.inventory_table.itemSelectionChanged.disconnect()
    window.inventory_table.itemSelectionChanged.connect(window.show_selected)
    window.inventory_save_listing_plan.clicked.connect(refresh_review)
    window.refresh_marketplace_listing_package_review = refresh_review
    refresh_review()
