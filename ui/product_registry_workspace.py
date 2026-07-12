from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.product_registry_lookup_service import ProductRegistryLookupService


class ProductRegistryWorkspace(QWidget):
    """Minimal read-only Product Registry operator workspace."""

    COLUMN_HEADERS = (
        'Product ID',
        'Type',
        'Canonical Name',
        'Set',
        'Card Number',
        'Variant',
        'State',
        'Matched By',
    )

    def __init__(self, lookup_service: ProductRegistryLookupService, parent=None):
        super().__init__(parent)
        self.lookup_service = lookup_service
        self.setObjectName('productRegistryWorkspace')

        title = QLabel('Product Registry')
        title.setObjectName('productRegistryTitle')

        self.search_input = QLineEdit()
        self.search_input.setObjectName('productRegistrySearchInput')
        self.search_input.setPlaceholderText('Search Product ID, name, alias, set, card number, or variant')
        self.search_input.returnPressed.connect(self.refresh_results)

        self.product_type_filter = QComboBox()
        self.product_type_filter.setObjectName('productRegistryTypeFilter')
        self.product_type_filter.addItem('All Types', None)
        self.product_type_filter.addItem('Singles', 'SINGLE')
        self.product_type_filter.addItem('Sealed', 'SEALED')

        self.search_button = QPushButton('Search')
        self.search_button.setObjectName('productRegistrySearchButton')
        self.search_button.clicked.connect(self.refresh_results)

        controls = QHBoxLayout()
        controls.addWidget(self.search_input, 1)
        controls.addWidget(self.product_type_filter)
        controls.addWidget(self.search_button)

        self.status_label = QLabel('Enter a search term to inspect registered products.')
        self.status_label.setObjectName('productRegistryStatusLabel')

        self.results_table = QTableWidget(0, len(self.COLUMN_HEADERS))
        self.results_table.setObjectName('productRegistryResultsTable')
        self.results_table.setHorizontalHeaderLabels(self.COLUMN_HEADERS)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSortingEnabled(False)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setStretchLastSection(True)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addLayout(controls)
        layout.addWidget(self.status_label)
        layout.addWidget(self.results_table, 1)

    def refresh_results(self) -> None:
        query = self.search_input.text()
        product_type = self.product_type_filter.currentData()
        results = self.lookup_service.search(query, product_type=product_type)

        self.results_table.setRowCount(len(results))
        for row_index, result in enumerate(results):
            values = (
                result.product_id,
                result.product_type,
                result.canonical_name,
                result.set_name or '',
                result.card_number or '',
                result.variant_name or '',
                result.state,
                result.matched_by,
            )
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.results_table.setItem(row_index, column_index, item)

        if not str(query or '').strip():
            self.status_label.setText('Enter a search term to inspect registered products.')
        elif results:
            suffix = '' if len(results) == 1 else 's'
            self.status_label.setText(f'{len(results)} product{suffix} found.')
        else:
            self.status_label.setText('No registered products matched this search.')
