import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path


class InventoryCsvImportService:
    REQUIRED_HEADERS = ['Asset ID','Asset Name','Asset Type','Quantity','Total Cost']
    ALLOWED_TYPES = {'SINGLE','SEALED','SLAB','ACCESSORY'}

    def __init__(self, inventory_service):
        self.inventory_service = inventory_service

    def validate_csv(self, source):
        source = Path(source)
        with source.open(newline='', encoding='utf-8-sig') as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != self.REQUIRED_HEADERS:
                raise ValueError('CSV headers must exactly match the MarketDEX inventory export format')
            rows = list(reader)
        if not rows:
            raise ValueError('CSV contains no inventory rows')
        validated = []
        seen_ids = set()
        existing_ids = {row['asset_id'] for row in self.inventory_service.list_inventory()}
        for line_number, row in enumerate(rows, start=2):
            asset_id = str(row['Asset ID'] or '').strip()
            asset_name = str(row['Asset Name'] or '').strip()
            asset_type = str(row['Asset Type'] or '').strip().upper()
            try:
                quantity = int(str(row['Quantity']).strip())
                cost = Decimal(str(row['Total Cost']).strip())
            except (ValueError, InvalidOperation):
                raise ValueError(f'Line {line_number}: Quantity and Total Cost must be numeric')
            if not asset_id or not asset_name:
                raise ValueError(f'Line {line_number}: Asset ID and Asset Name are required')
            if asset_type not in self.ALLOWED_TYPES:
                raise ValueError(f'Line {line_number}: unsupported Asset Type {asset_type}')
            if quantity < 0 or cost < 0 or cost.as_tuple().exponent < -2:
                raise ValueError(f'Line {line_number}: Quantity and Total Cost must be non-negative; cost supports two decimals')
            if asset_id in seen_ids:
                raise ValueError(f'Line {line_number}: duplicate Asset ID {asset_id}')
            if asset_id in existing_ids:
                raise ValueError(f'Line {line_number}: Asset ID already exists in MarketDEX: {asset_id}')
            seen_ids.add(asset_id)
            validated.append({'asset_id':asset_id,'asset_name':asset_name,'asset_type':asset_type,'quantity':quantity,'total_cost_minor':int(cost * 100)})
        return validated

    def import_csv(self, source, request_prefix):
        request_prefix = str(request_prefix or '').strip()
        if not request_prefix:
            raise ValueError('Import request identity is required')
        rows = self.validate_csv(source)
        imported = []
        for index, row in enumerate(rows):
            self.inventory_service.add_asset(**row, request_id=f'{request_prefix}-row-{index}')
            imported.append(row['asset_id'])
        return imported
