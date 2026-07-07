from services.mission_control_service import MissionControlService


def test_mission_control_snapshot_reads_protected_sqlite_authority(tmp_path):
    service = MissionControlService(tmp_path / 'marketdex.sqlite3')
    with service.database.transaction() as connection:
        connection.execute("INSERT INTO inventory_authority(asset_id,quantity,total_cost_minor,last_event_id,verified_at) VALUES (?,?,?,?,?)",('asset-1',3,12500,'event-inventory','2026-07-07T00:00:00Z'))
        connection.execute("INSERT INTO sales(sale_id,asset_id,quantity,revenue_minor,marketplace_fees_minor,shipping_minor,packaging_minor,cogs_minor,profit_minor,state,created_event_id,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",('sale-1','asset-1',1,7500,1000,500,100,4000,1900,'COMPLETED','event-sale','2026-07-07T00:00:00Z'))
        connection.execute("INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)",('event-audit','TEST_AUTHORITY','authority-1','VERIFIED','2026-07-07T00:00:00Z'))
        connection.execute("INSERT INTO event_identity(event_id,event_type,request_id,occurred_at,committed_at,payload_json,payload_sha256) VALUES (?,?,?,?,?,?,?)",('event-1','TEST_EVENT','request-1','2026-07-07T00:00:00Z','2026-07-07T00:00:00Z','{}','hash'))

    snapshot = service.snapshot()
    assert snapshot['inventory_units'] == 3
    assert snapshot['inventory_asset_count'] == 1
    assert snapshot['inventory_cost_minor'] == 12500
    assert snapshot['completed_sales'] == 1
    assert snapshot['revenue_minor'] == 7500
    assert snapshot['profit_minor'] == 1900
    assert snapshot['verified_audits'] == 1
    assert snapshot['authority_events'] == 1


def test_mission_control_snapshot_is_read_only(tmp_path):
    service = MissionControlService(tmp_path / 'marketdex.sqlite3')
    before = service.snapshot()
    after = service.snapshot()
    assert before == after
