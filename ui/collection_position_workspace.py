from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
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

from services.collection_position_service import CollectionPositionService


class CollectionPositionWorkspace(QWidget):
    """Read-only Collection Overview; no edit, valuation, or workflow actions."""

    COLUMN_HEADERS = (
        'Product', 'Product ID', 'Asset ID', 'Qty', 'Location',
        'Acquisition Date', 'Acquisition Source', 'Condition / Grade',
        'Collector Intent',
    )

    def __init__(self, service: CollectionPositionService, parent=None):
        super().__init__(parent)
        self.service = service
        self.setObjectName('collectionPositionWorkspace')

        title = QLabel('Collection Overview')
        title.setObjectName('collectionPositionTitle')
        subtitle = QLabel(
            'Read-only positions linked to the Product Registry. Classification fields remain unrecorded until their authority is approved.'
        )
        subtitle.setWordWrap(True)
        subtitle.setObjectName('collectionPositionSubtitle')

        self.search_input = QLineEdit()
        self.search_input.setObjectName('collectionPositionSearchInput')
        self.search_input.setPlaceholderText('Search product, product ID, asset ID, or location')
        self.search_input.returnPressed.connect(self.refresh_results)
        self.search_button = QPushButton('Refresh')
        self.search_button.setObjectName('collectionPositionRefreshButton')
        self.search_button.clicked.connect(self.refresh_results)
        controls = QHBoxLayout()
        controls.addWidget(self.search_input, 1)
        controls.addWidget(self.search_button)

        self.status_label = QLabel('No Collection positions loaded.')
        self.status_label.setObjectName('collectionPositionStatusLabel')
        self.results_table = QTableWidget(0, len(self.COLUMN_HEADERS))
        self.results_table.setObjectName('collectionPositionResultsTable')
        self.results_table.setHorizontalHeaderLabels(self.COLUMN_HEADERS)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setStretchLastSection(True)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(controls)
        layout.addWidget(self.status_label)
        layout.addWidget(self.results_table, 1)
        self.refresh_results()

    def refresh_results(self) -> None:
        results = self.service.list_positions(self.search_input.text())
        self.results_table.setRowCount(len(results))
        for row_index, result in enumerate(results):
            values = (
                result.canonical_name, result.product_id, result.asset_id,
                result.quantity, result.storage_location, result.purchase_date,
                result.purchase_source, result.condition_grade or 'Not recorded',
                result.collector_intent or 'Not recorded',
            )
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.results_table.setItem(row_index, column_index, item)
        query = self.search_input.text().strip()
        if query and not results:
            self.status_label.setText('No Collection positions matched this search.')
        elif results:
            self.status_label.setText(f'{len(results)} Collection position(s) found.')
        else:
            self.status_label.setText('No Collection positions are currently linked.')
