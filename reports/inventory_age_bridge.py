from reports.inventory_age import (
    EVIDENCE_AVAILABLE,
    InventoryAgeReportRow,
    derive_inventory_age_row,
)
from reports.inventory_age_input import InventoryAgeInputRecord
from reports.inventory_age_source import adapt_inventory_detail_purchase_date


def build_inventory_age_row_from_input(
    record: InventoryAgeInputRecord,
) -> InventoryAgeReportRow:
    """Build one read-only row from validated input without external access."""

    if not record.has_verified_product_link or record.product_id is None:
        raise ValueError('Inventory Age row requires verified product-link evidence')

    source_evidence = adapt_inventory_detail_purchase_date(
        {'purchase_date': record.purchase_date_raw}
    )
    if source_evidence.evidence_state == EVIDENCE_AVAILABLE:
        return derive_inventory_age_row(
            inventory_position_id=record.inventory_position_id,
            product_id=record.product_id,
            product_name=record.asset_name,
            current_quantity=record.current_quantity,
            inventory_status=record.inventory_status,
            as_of_date=record.as_of_date,
            source_start_date=source_evidence.source_date,
            storage_location=record.storage_location,
        )

    return InventoryAgeReportRow(
        inventory_position_id=record.inventory_position_id,
        product_id=record.product_id,
        product_name=record.asset_name,
        current_quantity=record.current_quantity,
        inventory_status=record.inventory_status,
        as_of_date=record.as_of_date,
        source_start_date=None,
        age_days=None,
        evidence_state=source_evidence.evidence_state,
        storage_location=record.storage_location,
        source_date_raw=source_evidence.raw_value,
        evidence_reason=source_evidence.reason,
    )
