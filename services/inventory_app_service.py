import csv
from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from repositories.inventory_repository import InventoryRepository
from services.base_service import AuthoritativeService

LISTING_STATUSES = ('Not Listed', 'Ready to List', 'Listed', 'Sold', 'Hold')
LISTING_READINESS_STATES = ('READY TO LIST', 'PREPARATION NEEDED', 'BLOCKED', 'NOT EVALUATED')
PHOTO_READINESS_STATES = ('Not Evaluated', 'Not Ready', 'Ready')
SHIPPING_PATHS = ('Not Evaluated', 'Standard Mail', 'Tracked Mail', 'Other')


def _derive_listing_readiness(detail):
    blockers = []
    if not str(detail.get('asset_name', '') or '').strip():
        blockers.append('Product identity is missing')
    if int(detail.get('quantity', 0) or 0) <= 0:
        blockers.append('Quantity must be greater than zero')
    if str(detail.get('item_condition', '') or '').strip().casefold() in {'', 'unknown', 'not evaluated'}:
        blockers.append('Condition must be evaluated')
    if not str(detail.get('marketplace', '') or '').strip():
        blockers.append('Marketplace is not selected')
    if int(detail.get('asking_price_minor', 0) or 0) <= 0:
        blockers.append('Asking price must be greater than $0.00')
    if not str(detail.get('sku', '') or '').strip():
        blockers.append('SKU is missing')
    if not str(detail.get('listing_title', '') or '').strip():
        blockers.append('Listing title is missing')
    if not str(detail.get('storage_location', '') or '').strip():
        blockers.append('Storage location is missing')
    photos_ready = str(detail.get('photos_ready', 'Not Evaluated') or '').strip()
    if photos_ready == 'Not Evaluated':
        blockers.append('Photo readiness is not evaluated')
    elif photos_ready != 'Ready':
        blockers.append('Photos are not ready')
    shipping_path = str(detail.get('shipping_path', 'Not Evaluated') or '').strip()
    if shipping_path == 'Not Evaluated':
        blockers.append('Shipping path is not reviewed')
    elif shipping_path not in SHIPPING_PATHS:
        blockers.append('Shipping path is not recognized')
    hard_blockers = {'Product identity is missing', 'Quantity must be greater than zero', 'Condition must be evaluated'}
    if not blockers:
        state = 'READY TO LIST'
    elif hard_blockers.intersection(blockers):
        state = 'BLOCKED'
    else:
        state = 'PREPARATION NEEDED'
    return {'readiness_state': state, 'readiness_blockers': blockers, 'readiness_blocker_count': len(blockers)}


class InventoryAppService(AuthoritativeService):
    service_name = 'inventory_app_service'

    def __init__(self, database_path):
        self.path = Path(database_path); database = DatabaseManager(self.path); database.initialize(); super().__init__(database, EventRepository()); self.inventory = InventoryRepository()

    def _list_inventory_state(self, state, search_text='', asset_type='ALL', item_condition='ALL', sort_key='NAME', sort_order='ASC', include_state=False, include_details=False, listing_status='ALL', marketplace='ALL', listing_queue=False):
        search_text = str(search_text or '').strip().casefold(); asset_type = str(asset_type or 'ALL').strip().upper(); item_condition = str(item_condition or 'ALL').strip(); sort_key = str(sort_key or 'NAME').strip().upper(); sort_order = str(sort_order or 'ASC').strip().upper(); listing_status = str(listing_status or 'ALL').strip(); marketplace = str(marketplace or 'ALL').strip(); listing_queue = bool(listing_queue)
        sort_fields = {'NAME':'asset_name','TYPE':'asset_type','QUANTITY':'quantity','TOTAL COST':'total_cost_minor'}
        if sort_key not in sort_fields: raise ValueError('Unsupported inventory sort key')
        if sort_order not in {'ASC','DESC'}: raise ValueError('Unsupported inventory sort order')
        if listing_status != 'ALL' and listing_status not in LISTING_STATUSES: raise ValueError('Unsupported listing status')
        if listing_queue: listing_status = 'Ready to List'
        listing_filter = listing_queue or listing_status != 'ALL' or marketplace != 'ALL'
        state_column = ',a.state' if include_state else ''
        detail_columns = ",COALESCE(b.storage_location,'') storage_location,COALESCE(b.notes,'') notes,COALESCE(m.product_name,'') product_name,COALESCE(m.set_name,'') set_name,COALESCE(m.item_condition,'') item_condition,COALESCE(m.market_price_minor,0) market_price_minor,COALESCE(NULLIF(l.sku,''),COALESCE(x.sku,'')) sku" if include_details else ''
        if include_details or listing_filter:
            detail_columns += ",COALESCE(l.listing_status,'Not Listed') listing_status,COALESCE(l.marketplace,'') marketplace,COALESCE(l.asking_price_minor,0) asking_price_minor,COALESCE(l.sku,'') listing_sku,COALESCE(l.listing_title,'') listing_title,COALESCE(l.listing_notes,'') listing_notes,COALESCE(p.photos_ready,'Not Evaluated') photos_ready,COALESCE(p.photo_reference,'') photo_reference,COALESCE(s.shipping_path,'Not Evaluated') shipping_path,COALESCE(s.shipping_notes,'') shipping_notes"
        detail_joins = ' LEFT JOIN inventory_business_details b ON b.asset_id=a.asset_id LEFT JOIN inventory_market_details m ON m.asset_id=a.asset_id LEFT JOIN inventory_import_details x ON x.asset_id=a.asset_id' if include_details else ''
        if include_details or listing_filter:
            detail_joins += ' LEFT JOIN inventory_listing_details l ON l.asset_id=a.asset_id'
        if include_details:
            detail_joins += ' LEFT JOIN inventory_listing_photo_evidence p ON p.asset_id=a.asset_id LEFT JOIN inventory_listing_shipping_evidence s ON s.asset_id=a.asset_id'
        with self.database.read_connection() as connection:
            rows = connection.execute(f"SELECT a.asset_id,a.asset_name,a.asset_type{state_column},i.quantity,i.total_cost_minor{detail_columns} FROM assets a JOIN inventory_authority i ON i.asset_id=a.asset_id{detail_joins} WHERE a.state=? ORDER BY a.asset_name COLLATE NOCASE,a.asset_id", (state,)).fetchall()
        inventory = [dict(row) for row in rows]
        if include_details:
            for row in inventory:
                row.update(_derive_listing_readiness(row))
        if search_text:
            inventory = [row for row in inventory if search_text in ' '.join(str(row.get(key, '')) for key in ('asset_name','product_name','set_name','asset_type','storage_location')).casefold()]
        if asset_type != 'ALL': inventory = [row for row in inventory if row['asset_type'] == asset_type]
        if item_condition != 'ALL': inventory = [row for row in inventory if row.get('item_condition', '') == item_condition]
        if listing_status != 'ALL': inventory = [row for row in inventory if row.get('listing_status', 'Not Listed') == listing_status]
        if marketplace != 'ALL': inventory = [row for row in inventory if row.get('marketplace', '') == marketplace]
        field = sort_fields[sort_key]
        def sort_value(row):
            value = row[field]; return value.casefold() if isinstance(value, str) else value
        inventory = sorted(inventory, key=lambda row:(sort_value(row), row['asset_id']), reverse=sort_order == 'DESC')
        if not include_details and listing_filter:
            keys = ['asset_id','asset_name','asset_type'] + (['state'] if include_state else []) + ['quantity','total_cost_minor']
            inventory = [{key: row[key] for key in keys} for row in inventory]
        return inventory

    def list_inventory(self, search_text='', asset_type='ALL', item_condition='ALL', sort_key='NAME', sort_order='ASC', include_details=False, listing_status='ALL', marketplace='ALL', listing_queue=False):
        return self._list_inventory_state('COMPLETED', search_text, asset_type, item_condition, sort_key, sort_order, include_details=include_details, listing_status=listing_status, marketplace=marketplace, listing_queue=listing_queue)

    def list_archived_inventory(self, search_text='', asset_type='ALL', item_condition='ALL', sort_key='NAME', sort_order='ASC', include_details=False, listing_status='ALL', marketplace='ALL', listing_queue=False):
        return self._list_inventory_state('CANCELLED', search_text, asset_type, item_condition, sort_key, sort_order, include_state=True, include_details=include_details, listing_status=listing_status, marketplace=marketplace, listing_queue=listing_queue)

    @staticmethod
    def summarize_inventory(rows):
        rows = list(rows); total_cost_minor = sum(int(row['total_cost_minor']) for row in rows); total_market_value_minor = sum(int(row.get('market_price_minor', 0)) * int(row['quantity']) for row in rows); return {'asset_count':len(rows),'total_units':sum(int(row['quantity']) for row in rows),'total_cost_minor':total_cost_minor,'total_market_value_minor':total_market_value_minor,'estimated_profit_minor':total_market_value_minor-total_cost_minor}

    @staticmethod
    def export_inventory_csv(rows, destination):
        destination = Path(destination)
        if destination.suffix.lower() != '.csv': destination = destination.with_suffix('.csv')
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('w', newline='', encoding='utf-8-sig') as handle:
            writer = csv.writer(handle); writer.writerow(['Asset ID','Asset Name','Asset Type','Quantity','Total Cost'])
            for row in rows: writer.writerow([row['asset_id'],row['asset_name'],row['asset_type'],int(row['quantity']),f"{int(row['total_cost_minor'])/100:.2f}"])
        return destination

    def export_listing_queue_csv(self, destination):
        destination = Path(destination)
        if destination.suffix.lower() != '.csv':
            destination = destination.with_suffix('.csv')
        destination.parent.mkdir(parents=True, exist_ok=True)
        rows = [
            row for row in self.list_inventory(include_details=True, listing_queue=True)
            if row.get('listing_status') == 'Ready to List' and row.get('readiness_state') == 'READY TO LIST'
        ]
        with destination.open('w', newline='', encoding='utf-8-sig') as handle:
            writer = csv.writer(handle)
            writer.writerow(['Asset ID', 'Listing Title', 'Marketplace', 'SKU', 'Condition', 'Asking Price', 'Quantity', 'Storage Location', 'Photos Ready', 'Photo Reference', 'Listing Notes', 'Shipping Path', 'Shipping Notes'])
            for row in rows:
                writer.writerow([
                    row['asset_id'], row.get('listing_title', ''), row.get('marketplace', ''), row.get('sku', ''),
                    row.get('item_condition', ''), f"{int(row.get('asking_price_minor', 0)) / 100:.2f}", int(row['quantity']),
                    row.get('storage_location', ''), row.get('photos_ready', 'Not Evaluated'), row.get('photo_reference', ''),
                    row.get('listing_notes', ''), row.get('shipping_path', 'Not Evaluated'), row.get('shipping_notes', ''),
                ])
        return destination

    def get_asset_detail(self, asset_id):
        with self.database.read_connection() as connection:
            row = connection.execute("SELECT a.asset_id,a.asset_name,a.asset_type,a.state,i.quantity,i.total_cost_minor,i.verified_at,COALESCE(b.purchase_date,'') purchase_date,COALESCE(b.purchase_source,'') purchase_source,COALESCE(b.storage_location,'') storage_location,COALESCE(b.notes,'') notes,COALESCE(m.product_name,'') product_name,COALESCE(m.set_name,'') set_name,COALESCE(m.item_condition,'') item_condition,COALESCE(m.market_price_minor,0) market_price_minor,COALESCE(NULLIF(l.sku,''),COALESCE(x.sku,'')) sku,COALESCE(l.listing_status,'Not Listed') listing_status,COALESCE(l.marketplace,'') marketplace,COALESCE(l.asking_price_minor,0) asking_price_minor,COALESCE(l.listing_title,'') listing_title,COALESCE(l.listing_notes,'') listing_notes,COALESCE(p.photos_ready,'Not Evaluated') photos_ready,COALESCE(p.photo_reference,'') photo_reference,COALESCE(s.shipping_path,'Not Evaluated') shipping_path,COALESCE(s.shipping_notes,'') shipping_notes FROM assets a JOIN inventory_authority i ON i.asset_id=a.asset_id LEFT JOIN inventory_business_details b ON b.asset_id=a.asset_id LEFT JOIN inventory_market_details m ON m.asset_id=a.asset_id LEFT JOIN inventory_import_details x ON x.asset_id=a.asset_id LEFT JOIN inventory_listing_details l ON l.asset_id=a.asset_id LEFT JOIN inventory_listing_photo_evidence p ON p.asset_id=a.asset_id LEFT JOIN inventory_listing_shipping_evidence s ON s.asset_id=a.asset_id WHERE a.asset_id=?", (asset_id,)).fetchone()
        if row is None: raise ValueError('Inventory asset not found')
        detail = dict(row)
        detail.update(_derive_listing_readiness(detail))
        return detail

    def add_asset(self, *, asset_id, asset_name, asset_type, quantity, total_cost_minor, request_id):
        asset_id = str(asset_id).strip(); asset_name = str(asset_name).strip(); asset_type = str(asset_type).strip().upper(); quantity = int(quantity); total_cost_minor = int(total_cost_minor)
        if not asset_id or not asset_name or not asset_type or quantity < 0 or total_cost_minor < 0: raise ValueError('Complete valid asset details are required')
        event = self._new_event('INVENTORY_ASSET_ADDED', request_id, {'asset_id':asset_id,'asset_name':asset_name,'asset_type':asset_type,'quantity':quantity,'total_cost_minor':total_cost_minor})
        with self.database.transaction() as connection:
            self._append_event_and_audit(connection, event, 'add_inventory_asset'); connection.execute("INSERT INTO assets(asset_id,asset_name,asset_type,state,created_event_id,created_at) VALUES (?,?,?,?,?,?)", (asset_id,asset_name,asset_type,'COMPLETED',event.event_id,event.committed_at)); self.inventory.apply(connection, asset_id=asset_id, quantity_delta=quantity, cost_delta_minor=total_cost_minor, event_id=event.event_id, recorded_at=event.committed_at); connection.execute("INSERT INTO inventory_movements(movement_id,asset_id,event_id,quantity_delta,cost_delta_minor,movement_type,recorded_at) VALUES (?,?,?,?,?,?,?)", (f'movement-{event.event_id}',asset_id,event.event_id,quantity,total_cost_minor,'ASSET_ADD',event.committed_at)); connection.execute("INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)", (event.event_id,'INVENTORY_ASSET',asset_id,'VERIFIED',event.committed_at)); self._verify_event(connection, event)
        return asset_id

    def update_business_details(self, *, asset_id, purchase_date='', purchase_source='', storage_location='', notes='', request_id):
        detail = self.get_asset_detail(asset_id)
        if detail['state'] != 'COMPLETED': raise ValueError('Archived inventory business details cannot be edited')
        values = {'purchase_date':str(purchase_date or '').strip(),'purchase_source':str(purchase_source or '').strip(),'storage_location':str(storage_location or '').strip(),'notes':str(notes or '').strip()}
        if all(detail[key] == value for key, value in values.items()): raise ValueError('Enter a business detail change')
        event = self._new_event('INVENTORY_BUSINESS_DETAILS_UPDATED', request_id, {'asset_id':asset_id, **values})
        with self.database.transaction() as connection:
            self._append_event_and_audit(connection, event, 'update_inventory_business_details')
            connection.execute("INSERT INTO inventory_business_details(asset_id,purchase_date,purchase_source,storage_location,notes,last_event_id,verified_at) VALUES (?,?,?,?,?,?,?) ON CONFLICT(asset_id) DO UPDATE SET purchase_date=excluded.purchase_date,purchase_source=excluded.purchase_source,storage_location=excluded.storage_location,notes=excluded.notes,last_event_id=excluded.last_event_id,verified_at=excluded.verified_at", (asset_id,values['purchase_date'],values['purchase_source'],values['storage_location'],values['notes'],event.event_id,event.committed_at))
            connection.execute("INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)", (event.event_id,'INVENTORY_BUSINESS_DETAILS',asset_id,'VERIFIED',event.committed_at)); self._verify_event(connection, event)
        return self.get_asset_detail(asset_id)

    def update_tcg_details(self, *, asset_id, product_name='', set_name='', item_condition='', market_price_minor=0, request_id):
        detail = self.get_asset_detail(asset_id)
        if detail['state'] != 'COMPLETED': raise ValueError('Archived inventory TCG details cannot be edited')
        values = {'product_name':str(product_name or '').strip(),'set_name':str(set_name or '').strip(),'item_condition':str(item_condition or '').strip(),'market_price_minor':int(market_price_minor or 0)}
        if values['market_price_minor'] < 0: raise ValueError('Market price cannot be negative')
        if all(detail[key] == value for key, value in values.items()): raise ValueError('Enter a TCG inventory detail change')
        event = self._new_event('INVENTORY_TCG_DETAILS_UPDATED', request_id, {'asset_id':asset_id, **values})
        with self.database.transaction() as connection:
            self._append_event_and_audit(connection, event, 'update_inventory_tcg_details')
            connection.execute("INSERT INTO inventory_market_details(asset_id,product_name,set_name,item_condition,market_price_minor,last_event_id,verified_at) VALUES (?,?,?,?,?,?,?) ON CONFLICT(asset_id) DO UPDATE SET product_name=excluded.product_name,set_name=excluded.set_name,item_condition=excluded.item_condition,market_price_minor=excluded.market_price_minor,last_event_id=excluded.last_event_id,verified_at=excluded.verified_at", (asset_id,values['product_name'],values['set_name'],values['item_condition'],values['market_price_minor'],event.event_id,event.committed_at))
            connection.execute("INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)", (event.event_id,'INVENTORY_TCG_DETAILS',asset_id,'VERIFIED',event.committed_at)); self._verify_event(connection, event)
        return self.get_asset_detail(asset_id)

    def update_asset(self, *, asset_id, asset_name, asset_type, quantity, total_cost_minor, product_name='', set_name='', item_condition='', market_price_minor=0, purchase_date='', purchase_source='', storage_location='', notes='', request_id):
        detail = self.get_asset_detail(asset_id); asset_name = str(asset_name or '').strip(); asset_type = str(asset_type or '').strip().upper(); quantity = int(quantity); total_cost_minor = int(total_cost_minor); market_price_minor = int(market_price_minor or 0)
        if detail['state'] != 'COMPLETED': raise ValueError('Archived inventory cannot be edited')
        if not asset_name or not asset_type or quantity < 0 or total_cost_minor < 0 or market_price_minor < 0: raise ValueError('Complete valid inventory details are required')
        values = {'asset_name':asset_name,'asset_type':asset_type,'quantity':quantity,'total_cost_minor':total_cost_minor,'product_name':str(product_name or '').strip(),'set_name':str(set_name or '').strip(),'item_condition':str(item_condition or '').strip(),'market_price_minor':market_price_minor,'purchase_date':str(purchase_date or '').strip(),'purchase_source':str(purchase_source or '').strip(),'storage_location':str(storage_location or '').strip(),'notes':str(notes or '').strip()}
        if all(detail.get(key) == value for key, value in values.items()): raise ValueError('Enter an inventory item change')
        event = self._new_event('INVENTORY_ASSET_UPDATED', request_id, {'asset_id':asset_id, **values})
        with self.database.transaction() as connection:
            self._append_event_and_audit(connection, event, 'update_inventory_asset')
            connection.execute("UPDATE assets SET asset_name=?,asset_type=? WHERE asset_id=?", (values['asset_name'],values['asset_type'],asset_id))
            quantity_delta = quantity - int(detail['quantity']); cost_delta_minor = total_cost_minor - int(detail['total_cost_minor'])
            if quantity_delta or cost_delta_minor:
                self.inventory.apply(connection, asset_id=asset_id, quantity_delta=quantity_delta, cost_delta_minor=cost_delta_minor, event_id=event.event_id, recorded_at=event.committed_at)
                connection.execute("INSERT INTO inventory_movements(movement_id,asset_id,event_id,quantity_delta,cost_delta_minor,movement_type,recorded_at) VALUES (?,?,?,?,?,?,?)", (f'movement-{event.event_id}',asset_id,event.event_id,quantity_delta,cost_delta_minor,'ASSET_EDIT',event.committed_at))
            connection.execute("INSERT INTO inventory_business_details(asset_id,purchase_date,purchase_source,storage_location,notes,last_event_id,verified_at) VALUES (?,?,?,?,?,?,?) ON CONFLICT(asset_id) DO UPDATE SET purchase_date=excluded.purchase_date,purchase_source=excluded.purchase_source,storage_location=excluded.storage_location,notes=excluded.notes,last_event_id=excluded.last_event_id,verified_at=excluded.verified_at", (asset_id,values['purchase_date'],values['purchase_source'],values['storage_location'],values['notes'],event.event_id,event.committed_at))
            connection.execute("INSERT INTO inventory_market_details(asset_id,product_name,set_name,item_condition,market_price_minor,last_event_id,verified_at) VALUES (?,?,?,?,?,?,?) ON CONFLICT(asset_id) DO UPDATE SET product_name=excluded.product_name,set_name=excluded.set_name,item_condition=excluded.item_condition,market_price_minor=excluded.market_price_minor,last_event_id=excluded.last_event_id,verified_at=excluded.verified_at", (asset_id,values['product_name'],values['set_name'],values['item_condition'],values['market_price_minor'],event.event_id,event.committed_at))
            connection.execute("INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)", (event.event_id,'INVENTORY_ASSET_UPDATE',asset_id,'VERIFIED',event.committed_at)); self._verify_event(connection, event)
        return self.get_asset_detail(asset_id)

    def get_listing_readiness(self, asset_id):
        detail = self.get_asset_detail(asset_id)
        return {key: detail[key] for key in ('readiness_state', 'readiness_blockers', 'readiness_blocker_count')}

    def update_listing_details(self, *, asset_id, listing_status='Not Listed', marketplace='', asking_price_minor=0, sku='', storage_location='', listing_title='', listing_notes='', photos_ready=None, photo_reference=None, shipping_path=None, shipping_notes=None, request_id):
        detail = self.get_asset_detail(asset_id)
        if detail['state'] != 'COMPLETED': raise ValueError('Archived inventory listing details cannot be edited')
        photo_state = detail.get('photos_ready', 'Not Evaluated') if photos_ready is None else photos_ready
        photo_reference_value = detail.get('photo_reference', '') if photo_reference is None else photo_reference
        shipping_path_value = detail.get('shipping_path', 'Not Evaluated') if shipping_path is None else shipping_path
        shipping_notes_value = detail.get('shipping_notes', '') if shipping_notes is None else shipping_notes
        values = {'listing_status':str(listing_status or '').strip(),'marketplace':str(marketplace or '').strip(),'asking_price_minor':int(asking_price_minor or 0),'sku':str(sku or '').strip(),'storage_location':str(storage_location or '').strip(),'listing_title':str(listing_title or '').strip(),'listing_notes':str(listing_notes or '').strip(),'photos_ready':str(photo_state or '').strip(),'photo_reference':str(photo_reference_value or '').strip(),'shipping_path':str(shipping_path_value or '').strip(),'shipping_notes':str(shipping_notes_value or '').strip()}
        if values['listing_status'] not in LISTING_STATUSES: raise ValueError('Choose a valid listing status')
        if values['photos_ready'] not in PHOTO_READINESS_STATES: raise ValueError('Choose a valid photo readiness value')
        if values['shipping_path'] not in SHIPPING_PATHS: raise ValueError('Choose a valid shipping path value')
        if values['asking_price_minor'] < 0: raise ValueError('Asking price cannot be negative')
        candidate = {**detail, **values}
        readiness = _derive_listing_readiness(candidate)
        if values['listing_status'] == 'Ready to List' and readiness['readiness_blockers']:
            raise ValueError('Ready to List blocked: ' + '; '.join(readiness['readiness_blockers']))
        if all(detail.get(key, '') == value for key, value in values.items()): raise ValueError('Enter a listing detail change')
        event = self._new_event('INVENTORY_LISTING_DETAILS_UPDATED', request_id, {'asset_id':asset_id, **values})
        with self.database.transaction() as connection:
            self._append_event_and_audit(connection, event, 'update_inventory_listing_details')
            connection.execute("INSERT INTO inventory_listing_details(asset_id,listing_status,marketplace,asking_price_minor,sku,listing_title,listing_notes,last_event_id,verified_at) VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT(asset_id) DO UPDATE SET listing_status=excluded.listing_status,marketplace=excluded.marketplace,asking_price_minor=excluded.asking_price_minor,sku=excluded.sku,listing_title=excluded.listing_title,listing_notes=excluded.listing_notes,last_event_id=excluded.last_event_id,verified_at=excluded.verified_at", (asset_id,values['listing_status'],values['marketplace'],values['asking_price_minor'],values['sku'],values['listing_title'],values['listing_notes'],event.event_id,event.committed_at))
            connection.execute("INSERT INTO inventory_listing_photo_evidence(asset_id,photos_ready,photo_reference,last_event_id,verified_at) VALUES (?,?,?,?,?) ON CONFLICT(asset_id) DO UPDATE SET photos_ready=excluded.photos_ready,photo_reference=excluded.photo_reference,last_event_id=excluded.last_event_id,verified_at=excluded.verified_at", (asset_id,values['photos_ready'],values['photo_reference'],event.event_id,event.committed_at))
            connection.execute("INSERT INTO inventory_listing_shipping_evidence(asset_id,shipping_path,shipping_notes,last_event_id,verified_at) VALUES (?,?,?,?,?) ON CONFLICT(asset_id) DO UPDATE SET shipping_path=excluded.shipping_path,shipping_notes=excluded.shipping_notes,last_event_id=excluded.last_event_id,verified_at=excluded.verified_at", (asset_id,values['shipping_path'],values['shipping_notes'],event.event_id,event.committed_at))
            connection.execute("INSERT INTO inventory_business_details(asset_id,purchase_date,purchase_source,storage_location,notes,last_event_id,verified_at) VALUES (?,?,?,?,?,?,?) ON CONFLICT(asset_id) DO UPDATE SET storage_location=excluded.storage_location,last_event_id=excluded.last_event_id,verified_at=excluded.verified_at", (asset_id,detail['purchase_date'],detail['purchase_source'],values['storage_location'],detail['notes'],event.event_id,event.committed_at))
            connection.execute("INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)", (event.event_id,'INVENTORY_LISTING_DETAILS',asset_id,'VERIFIED',event.committed_at))
            self._verify_event(connection, event)
        return self.get_asset_detail(asset_id)

    def delete_asset(self, *, asset_id, request_id):
        return self.archive_asset(asset_id=asset_id, request_id=request_id)

    def list_item_activity(self, asset_id):
        self.get_asset_detail(asset_id)
        with self.database.read_connection() as connection:
            rows=connection.execute("SELECT recorded_at,adjustment_type,quantity_delta,reason,resulting_quantity FROM inventory_adjustment_activity WHERE asset_id=? ORDER BY recorded_at DESC,activity_id DESC", (asset_id,)).fetchall()
        return [dict(row) for row in rows]

    def record_adjustment(self, *, asset_id, adjustment_type, quantity_delta, reason, request_id):
        adjustment_type=str(adjustment_type or '').strip().upper(); quantity_delta=int(quantity_delta); reason=str(reason or '').strip()
        allowed={'ADD_STOCK','REMOVE_STOCK','CORRECTION','DAMAGED','SOLD_OUTSIDE_PLATFORM'}
        if adjustment_type not in allowed: raise ValueError('Choose an adjustment type')
        if not reason: raise ValueError('Enter an adjustment reason')
        if quantity_delta == 0: raise ValueError('Enter a quantity change')
        if adjustment_type == 'ADD_STOCK' and quantity_delta < 0: raise ValueError('Add stock must increase quantity')
        if adjustment_type in {'REMOVE_STOCK','DAMAGED','SOLD_OUTSIDE_PLATFORM'} and quantity_delta > 0: raise ValueError('This adjustment type must decrease quantity')
        detail=self.get_asset_detail(asset_id)
        if detail['state'] != 'COMPLETED': raise ValueError('Archived inventory cannot be adjusted')
        if int(detail['quantity']) + quantity_delta < 0: raise ValueError('Adjustment would make quantity negative')
        event=self._new_event('INVENTORY_TYPED_ADJUSTMENT',request_id,{'asset_id':asset_id,'adjustment_type':adjustment_type,'quantity_delta':quantity_delta,'reason':reason})
        with self.database.transaction() as connection:
            self._append_event_and_audit(connection,event,'record_inventory_adjustment')
            self.inventory.apply(connection,asset_id=asset_id,quantity_delta=quantity_delta,cost_delta_minor=0,event_id=event.event_id,recorded_at=event.committed_at)
            resulting=connection.execute("SELECT quantity FROM inventory_authority WHERE asset_id=?",(asset_id,)).fetchone()['quantity']
            connection.execute("INSERT INTO inventory_movements(movement_id,asset_id,event_id,quantity_delta,cost_delta_minor,movement_type,recorded_at) VALUES (?,?,?,?,?,?,?)",(f'movement-{event.event_id}',asset_id,event.event_id,quantity_delta,0,adjustment_type,event.committed_at))
            connection.execute("INSERT INTO inventory_adjustment_activity(activity_id,asset_id,event_id,adjustment_type,quantity_delta,reason,resulting_quantity,recorded_at) VALUES (?,?,?,?,?,?,?,?)",(f'activity-{event.event_id}',asset_id,event.event_id,adjustment_type,quantity_delta,reason,resulting,event.committed_at))
            connection.execute("INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)",(event.event_id,'INVENTORY_ADJUSTMENT',asset_id,'VERIFIED',event.committed_at)); self._verify_event(connection,event)
        return self.get_asset_detail(asset_id)

    def adjust_asset(self, *, asset_id, quantity_delta, cost_delta_minor, request_id):
        quantity_delta = int(quantity_delta); cost_delta_minor = int(cost_delta_minor)
        if quantity_delta == 0 and cost_delta_minor == 0: raise ValueError('Enter a quantity or cost adjustment')
        detail = self.get_asset_detail(asset_id)
        if detail['state'] != 'COMPLETED': raise ValueError('Archived inventory cannot be adjusted')
        event = self._new_event('INVENTORY_ASSET_ADJUSTED', request_id, {'asset_id':asset_id,'quantity_delta':quantity_delta,'cost_delta_minor':cost_delta_minor})
        with self.database.transaction() as connection:
            self._append_event_and_audit(connection, event, 'adjust_inventory_asset'); self.inventory.apply(connection, asset_id=asset_id, quantity_delta=quantity_delta, cost_delta_minor=cost_delta_minor, event_id=event.event_id, recorded_at=event.committed_at); connection.execute("INSERT INTO inventory_movements(movement_id,asset_id,event_id,quantity_delta,cost_delta_minor,movement_type,recorded_at) VALUES (?,?,?,?,?,?,?)", (f'movement-{event.event_id}',asset_id,event.event_id,quantity_delta,cost_delta_minor,'MANUAL_ADJUSTMENT',event.committed_at)); connection.execute("INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)", (event.event_id,'INVENTORY_ADJUSTMENT',asset_id,'VERIFIED',event.committed_at)); self._verify_event(connection, event)
        return self.get_asset_detail(asset_id)

    def bulk_adjust_assets(self, *, asset_ids, quantity_delta, cost_delta_minor, request_prefix):
        asset_ids = list(dict.fromkeys(str(asset_id).strip() for asset_id in asset_ids if str(asset_id).strip())); quantity_delta = int(quantity_delta); cost_delta_minor = int(cost_delta_minor); request_prefix = str(request_prefix or '').strip()
        if not asset_ids: raise ValueError('Select at least one inventory asset')
        if quantity_delta == 0 and cost_delta_minor == 0: raise ValueError('Enter a quantity or cost adjustment')
        if not request_prefix: raise ValueError('Bulk adjustment request identity is required')
        details = [self.get_asset_detail(asset_id) for asset_id in asset_ids]
        for detail in details:
            if detail['state'] != 'COMPLETED': raise ValueError(f"Archived inventory cannot be adjusted: {detail['asset_name']}")
            if int(detail['quantity']) + quantity_delta < 0: raise ValueError(f"Bulk adjustment would make quantity negative: {detail['asset_name']}")
            if int(detail['total_cost_minor']) + cost_delta_minor < 0: raise ValueError(f"Bulk adjustment would make cost negative: {detail['asset_name']}")
        adjusted = []
        for index, asset_id in enumerate(asset_ids): self.adjust_asset(asset_id=asset_id, quantity_delta=quantity_delta, cost_delta_minor=cost_delta_minor, request_id=f'{request_prefix}-asset-{index}'); adjusted.append(asset_id)
        return adjusted

    def archive_asset(self, *, asset_id, request_id):
        detail = self.get_asset_detail(asset_id)
        if detail['state'] != 'COMPLETED': raise ValueError('Inventory asset is already archived')
        event = self._new_event('INVENTORY_ASSET_ARCHIVED', request_id, {'asset_id':asset_id,'previous_state':'COMPLETED','archive_state':'CANCELLED'})
        with self.database.transaction() as connection:
            self._append_event_and_audit(connection, event, 'archive_inventory_asset'); connection.execute("UPDATE assets SET state='CANCELLED' WHERE asset_id=? AND state='COMPLETED'", (asset_id,)); connection.execute("INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)", (event.event_id,'INVENTORY_ARCHIVE',asset_id,'VERIFIED',event.committed_at)); self._verify_event(connection, event)
        return self.get_asset_detail(asset_id)

    def restore_asset(self, *, asset_id, request_id):
        detail = self.get_asset_detail(asset_id)
        if detail['state'] != 'CANCELLED': raise ValueError('Only archived inventory can be restored')
        event = self._new_event('INVENTORY_ASSET_RESTORED', request_id, {'asset_id':asset_id,'previous_state':'CANCELLED','restore_state':'COMPLETED'})
        with self.database.transaction() as connection:
            self._append_event_and_audit(connection, event, 'restore_inventory_asset'); connection.execute("UPDATE assets SET state='COMPLETED' WHERE asset_id=? AND state='CANCELLED'", (asset_id,)); connection.execute("INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)", (event.event_id,'INVENTORY_RESTORE',asset_id,'VERIFIED',event.committed_at)); self._verify_event(connection, event)
        return self.get_asset_detail(asset_id)
