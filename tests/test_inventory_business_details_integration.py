from services.inventory_app_service import InventoryAppService


def test_business_details_are_authoritative_without_changing_inventory_truth(tmp_path):
    service = InventoryAppService(tmp_path / 'marketdex.sqlite3')
    service.add_asset(asset_id='asset-1', asset_name='Charizard ex', asset_type='SINGLE', quantity=3, total_cost_minor=1200, request_id='add-1')

    before = service.get_asset_detail('asset-1')
    updated = service.update_business_details(
        asset_id='asset-1',
        purchase_date='2026-07-08',
        purchase_source='Local Card Shop',
        storage_location='Binder A / Page 3',
        notes='Grade candidate',
        request_id='business-details-1',
    )

    assert updated['purchase_date'] == '2026-07-08'
    assert updated['purchase_source'] == 'Local Card Shop'
    assert updated['storage_location'] == 'Binder A / Page 3'
    assert updated['notes'] == 'Grade candidate'
    assert updated['quantity'] == before['quantity'] == 3
    assert updated['total_cost_minor'] == before['total_cost_minor'] == 1200

    with service.database.read_connection() as connection:
        event = connection.execute("SELECT event_type FROM event_identity WHERE request_id='business-details-1'").fetchone()
        audit = connection.execute("SELECT verification_result FROM audit_events WHERE authority_type='INVENTORY_BUSINESS_DETAILS' AND authority_id='asset-1'").fetchone()
        movements = connection.execute("SELECT COUNT(*) count FROM inventory_movements WHERE asset_id='asset-1'").fetchone()['count']
    assert event['event_type'] == 'INVENTORY_BUSINESS_DETAILS_UPDATED'
    assert audit['verification_result'] == 'VERIFIED'
    assert movements == 1


def test_business_details_reject_noop_and_archived_asset(tmp_path):
    service = InventoryAppService(tmp_path / 'marketdex.sqlite3')
    service.add_asset(asset_id='asset-1', asset_name='ETB', asset_type='SEALED', quantity=1, total_cost_minor=5000, request_id='add-1')

    try:
        service.update_business_details(asset_id='asset-1', request_id='noop-1')
        assert False, 'no-op edit must be rejected'
    except ValueError as exc:
        assert 'business detail change' in str(exc)

    service.archive_asset(asset_id='asset-1', request_id='archive-1')
    try:
        service.update_business_details(asset_id='asset-1', notes='changed', request_id='archived-edit-1')
        assert False, 'archived edit must be rejected'
    except ValueError as exc:
        assert 'Archived inventory business details' in str(exc)
