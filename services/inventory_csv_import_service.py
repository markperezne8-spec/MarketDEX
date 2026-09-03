import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from uuid import uuid4


class InventoryCsvImportService:
    REQUIRED_HEADERS = {'Item Name','Category','Quantity','Condition','Cost','Market Price','Storage Location'}
    OPTIONAL_HEADERS = {'Set / Product','Notes','SKU'}
    ALLOWED_TYPES = {'SINGLE','SEALED','SLAB','ACCESSORY'}

    def __init__(self, inventory_service):
        self.inventory_service = inventory_service

    @staticmethod
    def _minor(value, label):
        try: amount = Decimal(str(value or '').strip())
        except (InvalidOperation, ValueError): raise ValueError(f'{label} must be numeric')
        if amount < 0 or amount.as_tuple().exponent < -2: raise ValueError(f'{label} must be non-negative with at most two decimals')
        return int(amount * 100)

    def preview_csv(self, source):
        source = Path(source)
        with source.open(newline='', encoding='utf-8-sig') as handle:
            reader = csv.DictReader(handle)
            headers = set(reader.fieldnames or [])
            missing = self.REQUIRED_HEADERS - headers
            if missing: raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")
            rows = list(reader)
        valid, errors, seen = [], [], set()
        for line_number, row in enumerate(rows, start=2):
            try:
                item_name = str(row.get('Item Name') or '').strip()
                asset_type = str(row.get('Category') or '').strip().upper()
                item_condition = str(row.get('Condition') or '').strip()
                storage_location = str(row.get('Storage Location') or '').strip()
                quantity = int(str(row.get('Quantity') or '').strip())
                if not item_name or not item_condition or not storage_location: raise ValueError('Item Name, Condition, and Storage Location are required')
                if asset_type not in self.ALLOWED_TYPES: raise ValueError(f'unsupported Category {asset_type}')
                if quantity < 0: raise ValueError('Quantity must be non-negative')
                total_cost_minor = self._minor(row.get('Cost'), 'Cost')
                market_price_minor = self._minor(row.get('Market Price'), 'Market Price')
                signature = (item_name.casefold(), str(row.get('Set / Product') or '').strip().casefold(), asset_type, item_condition.casefold(), storage_location.casefold())
                if signature in seen: raise ValueError('duplicate inventory row in this file')
                seen.add(signature)
                valid.append({'asset_name':item_name,'asset_type':asset_type,'quantity':quantity,'total_cost_minor':total_cost_minor,'product_name':item_name,'set_name':str(row.get('Set / Product') or '').strip(),'item_condition':item_condition,'market_price_minor':market_price_minor,'storage_location':storage_location,'notes':str(row.get('Notes') or '').strip(),'sku':str(row.get('SKU') or '').strip(),'line_number':line_number})
            except ValueError as exc: errors.append(f'Line {line_number}: {exc}')
        return {'total_rows':len(rows),'valid_rows':valid,'skipped_rows':len(errors),'errors':errors}

    def import_csv(self, source, request_prefix):
        request_prefix = str(request_prefix or '').strip()
        if not request_prefix: raise ValueError('Import request identity is required')
        preview = self.preview_csv(source); imported = []
        for row in preview['valid_rows']:
            try:
                asset_id = f'asset-{uuid4().hex}'
                self.inventory_service.add_asset(asset_id=asset_id,asset_name=row['asset_name'],asset_type=row['asset_type'],quantity=row['quantity'],total_cost_minor=row['total_cost_minor'],request_id=f"{request_prefix}-line-{row['line_number']}")
                self.inventory_service.update_business_details(asset_id=asset_id,storage_location=row['storage_location'],notes=row['notes'],request_id=f"{request_prefix}-business-{row['line_number']}")
                self.inventory_service.update_tcg_details(asset_id=asset_id,product_name=row['product_name'],set_name=row['set_name'],item_condition=row['item_condition'],market_price_minor=row['market_price_minor'],request_id=f"{request_prefix}-tcg-{row['line_number']}")
                detail = self.inventory_service.get_asset_detail(asset_id)
                event = self.inventory_service._new_event('INVENTORY_IMPORT_SKU_SET', f"{request_prefix}-sku-{row['line_number']}", {'asset_id':asset_id,'sku':row['sku']})
                with self.inventory_service.database.transaction() as connection:
                    self.inventory_service._append_event_and_audit(connection, event, 'set_inventory_import_sku')
                    connection.execute("INSERT INTO inventory_import_details(asset_id,sku,last_event_id,verified_at) VALUES (?,?,?,?)", (asset_id,row['sku'],event.event_id,event.committed_at))
                    connection.execute("INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)", (event.event_id,'INVENTORY_IMPORT_SKU',asset_id,'VERIFIED',event.committed_at)); self.inventory_service._verify_event(connection,event)
                imported.append(asset_id)
            except Exception as exc: preview['errors'].append(f"Line {row['line_number']}: {exc}"); preview['skipped_rows'] += 1
        return {'total_rows':preview['total_rows'],'imported_rows':len(imported),'skipped_rows':preview['skipped_rows'],'errors':preview['errors'],'asset_ids':imported}
