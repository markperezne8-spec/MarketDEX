import pytest
from services.inventory_app_service import InventoryAppService


def _inventory(tmp_path):
    service=InventoryAppService(tmp_path/'marketdex.sqlite3')
    service.add_asset(asset_id='asset-1',asset_name='Charizard ex',asset_type='SINGLE',quantity=2,total_cost_minor=2500,request_id='seed-1')
    service.add_asset(asset_id='asset-2',asset_name='Mega Evolution ETB',asset_type='SEALED',quantity=3,total_cost_minor=18000,request_id='seed-2')
    return service


def test_bulk_adjust_applies_same_delta_through_authoritative_events(tmp_path):
    service=_inventory(tmp_path)
    adjusted=service.bulk_adjust_assets(asset_ids=['asset-1','asset-2'],quantity_delta=2,cost_delta_minor=150,request_prefix='bulk-1')
    assert adjusted==['asset-1','asset-2']
    assert service.get_asset_detail('asset-1')['quantity']==4
    assert service.get_asset_detail('asset-1')['total_cost_minor']==2650
    assert service.get_asset_detail('asset-2')['quantity']==5
    assert service.get_asset_detail('asset-2')['total_cost_minor']==18150
    with service.database.read_connection() as connection:
        assert connection.execute("SELECT COUNT(*) n FROM event_identity WHERE event_type='INVENTORY_ASSET_ADJUSTED'").fetchone()['n']==2
        assert connection.execute("SELECT COUNT(*) n FROM inventory_movements WHERE movement_type='MANUAL_ADJUSTMENT'").fetchone()['n']==2
        assert connection.execute("SELECT COUNT(*) n FROM audit_events WHERE authority_type='INVENTORY_ADJUSTMENT' AND verification_result='VERIFIED'").fetchone()['n']==2


def test_bulk_adjust_validates_complete_selection_before_mutation(tmp_path):
    service=_inventory(tmp_path)
    with pytest.raises(ValueError,match='quantity negative'):
        service.bulk_adjust_assets(asset_ids=['asset-1','asset-2'],quantity_delta=-3,cost_delta_minor=0,request_prefix='bulk-blocked')
    assert service.get_asset_detail('asset-1')['quantity']==2
    assert service.get_asset_detail('asset-2')['quantity']==3
    with service.database.read_connection() as connection:
        assert connection.execute("SELECT COUNT(*) n FROM event_identity WHERE event_type='INVENTORY_ASSET_ADJUSTED'").fetchone()['n']==0


def test_bulk_adjust_rejects_empty_selection_zero_delta_and_missing_identity(tmp_path):
    service=_inventory(tmp_path)
    with pytest.raises(ValueError,match='Select at least one'):
        service.bulk_adjust_assets(asset_ids=[],quantity_delta=1,cost_delta_minor=0,request_prefix='bulk')
    with pytest.raises(ValueError,match='quantity or cost adjustment'):
        service.bulk_adjust_assets(asset_ids=['asset-1'],quantity_delta=0,cost_delta_minor=0,request_prefix='bulk')
    with pytest.raises(ValueError,match='request identity'):
        service.bulk_adjust_assets(asset_ids=['asset-1'],quantity_delta=1,cost_delta_minor=0,request_prefix='')


def test_bulk_adjust_deduplicates_selected_asset_ids(tmp_path):
    service=_inventory(tmp_path)
    adjusted=service.bulk_adjust_assets(asset_ids=['asset-1','asset-1','asset-2'],quantity_delta=1,cost_delta_minor=0,request_prefix='bulk-dedupe')
    assert adjusted==['asset-1','asset-2']
    assert service.get_asset_detail('asset-1')['quantity']==3
    assert service.get_asset_detail('asset-2')['quantity']==4