import pytest
from core.event_repository import ReplayRejected
from services.inventory_app_service import InventoryAppService


def _service(tmp_path):
    service=InventoryAppService(tmp_path/'marketdex.sqlite3')
    service.add_asset(asset_id='asset-1',asset_name='Mega Evolution ETB',asset_type='SEALED',quantity=2,total_cost_minor=13000,request_id='add-1')
    return service


def test_asset_detail_reads_authoritative_inventory(tmp_path):
    detail=_service(tmp_path).get_asset_detail('asset-1')
    assert detail['asset_name']=='Mega Evolution ETB'
    assert detail['quantity']==2 and detail['total_cost_minor']==13000


def test_adjust_asset_updates_projection_and_appends_evidence(tmp_path):
    service=_service(tmp_path)
    detail=service.adjust_asset(asset_id='asset-1',quantity_delta=3,cost_delta_minor=15000,request_id='adjust-1')
    assert detail['quantity']==5 and detail['total_cost_minor']==28000
    with service.database.read_connection() as c:
        assert c.execute("SELECT COUNT(*) n FROM inventory_history WHERE asset_id='asset-1'").fetchone()['n']==2
        movement=c.execute("SELECT * FROM inventory_movements WHERE movement_type='MANUAL_ADJUSTMENT'").fetchone()
        assert movement['quantity_delta']==3 and movement['cost_delta_minor']==15000
        assert c.execute("SELECT verification_result FROM audit_events WHERE event_id=?",(movement['event_id'],)).fetchone()['verification_result']=='VERIFIED'


def test_adjust_asset_blocks_negative_authority_and_rolls_back(tmp_path):
    service=_service(tmp_path)
    with pytest.raises(ValueError,match='Quantity cannot become negative'):
        service.adjust_asset(asset_id='asset-1',quantity_delta=-3,cost_delta_minor=0,request_id='adjust-negative')
    assert service.get_asset_detail('asset-1')['quantity']==2


def test_adjust_asset_request_identity_is_exactly_once(tmp_path):
    service=_service(tmp_path)
    service.adjust_asset(asset_id='asset-1',quantity_delta=1,cost_delta_minor=500,request_id='adjust-1')
    with pytest.raises(ReplayRejected):
        service.adjust_asset(asset_id='asset-1',quantity_delta=2,cost_delta_minor=500,request_id='adjust-1')
    assert service.get_asset_detail('asset-1')['quantity']==3


def test_zero_adjustment_is_blocked(tmp_path):
    service=_service(tmp_path)
    with pytest.raises(ValueError,match='Enter a quantity or cost adjustment'):
        service.adjust_asset(asset_id='asset-1',quantity_delta=0,cost_delta_minor=0,request_id='adjust-zero')
