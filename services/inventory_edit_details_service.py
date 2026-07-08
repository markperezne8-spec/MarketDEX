ALLOWED_ASSET_TYPES = {'SINGLE', 'SEALED', 'SLAB', 'ACCESSORY'}


def edit_inventory_details(service, *, asset_id, asset_name, asset_type, request_id):
    detail = service.get_asset_detail(asset_id)
    if detail['state'] != 'COMPLETED':
        raise ValueError('Archived inventory details cannot be edited')
    asset_name = str(asset_name or '').strip()
    asset_type = str(asset_type or '').strip().upper()
    if not asset_name:
        raise ValueError('Asset name is required')
    if asset_type not in ALLOWED_ASSET_TYPES:
        raise ValueError('Unsupported asset type')
    if asset_name == detail['asset_name'] and asset_type == detail['asset_type']:
        raise ValueError('Change the asset name or type')
    event = service._new_event('INVENTORY_ASSET_DETAILS_EDITED', request_id, {
        'asset_id': asset_id,
        'previous_asset_name': detail['asset_name'],
        'previous_asset_type': detail['asset_type'],
        'asset_name': asset_name,
        'asset_type': asset_type,
    })
    with service.database.transaction() as connection:
        service._append_event_and_audit(connection, event, 'edit_inventory_asset_details')
        connection.execute(
            "UPDATE assets SET asset_name=?,asset_type=? WHERE asset_id=? AND state='COMPLETED'",
            (asset_name, asset_type, asset_id),
        )
        connection.execute(
            "INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)",
            (event.event_id, 'INVENTORY_DETAILS_EDIT', asset_id, 'VERIFIED', event.committed_at),
        )
        service._verify_event(connection, event)
    return service.get_asset_detail(asset_id)
