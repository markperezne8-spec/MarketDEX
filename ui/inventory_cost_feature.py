from PySide6.QtWidgets import QLabel, QTableWidgetItem


def unit_cost_minor(row):
    quantity = int(row['quantity'])
    return 0 if quantity <= 0 else round(int(row['total_cost_minor']) / quantity)


def intake_quality(detail):
    fields = ('purchase_date', 'purchase_source', 'storage_location', 'notes')
    completed = sum(bool(str(detail.get(field) or '').strip()) for field in fields)
    return completed, len(fields)


def install_inventory_cost_feature(window):
    table = window.inventory_table
    table.setColumnCount(5)
    table.setHorizontalHeaderLabels(['Asset', 'Type', 'Qty', 'Total Cost', 'Unit Cost'])

    quality = QLabel('INTAKE QUALITY: Select one inventory asset.')
    quality.setWordWrap(True)
    window.inventory_intake_quality = quality
    panel_layout = window.inventory_panel.layout()
    panel_layout.insertWidget(panel_layout.indexOf(window.asset_detail) + 1, quality)

    original_refresh_inventory = window.refresh_inventory
    original_show_selected = window.show_selected

    def refresh_inventory():
        original_refresh_inventory()
        for row_index, row in enumerate(window.inventory_rows):
            table.setItem(row_index, 4, QTableWidgetItem(window._money(unit_cost_minor(row))))
        table.resizeColumnsToContents()

    def show_selected():
        original_show_selected()
        asset_id = window.selected_asset_id()
        if asset_id is None:
            quality.setText('INTAKE QUALITY: Select one inventory asset.')
            return
        detail = window.inventory_service.get_asset_detail(asset_id)
        completed, total = intake_quality(detail)
        missing = [label for key, label in (
            ('purchase_date', 'Purchase Date'),
            ('purchase_source', 'Purchase Source'),
            ('storage_location', 'Storage Location'),
            ('notes', 'Notes'),
        ) if not str(detail.get(key) or '').strip()]
        status = 'COMPLETE' if not missing else 'NEEDS DETAILS'
        suffix = '' if not missing else f" • Missing: {', '.join(missing)}"
        quality.setText(f'INTAKE QUALITY: {status} • {completed}/{total} business details{suffix}')

    window.refresh_inventory = refresh_inventory
    window.show_selected = show_selected
    table.itemSelectionChanged.disconnect()
    table.itemSelectionChanged.connect(window.show_selected)
    window.refresh_inventory()
