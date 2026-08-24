from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
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
from ui.design_system.widgets import MarketDEXKpiCard


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

        self.authority_card = MarketDEXKpiCard(
            'Collection Position Projection',
            'READ-ONLY',
        )
        self.authority_card.setProperty('dashboardRole', 'inventory-command-summary')
        self.authority_card.set_comparison('AUTHORITY GATE')
        self.authority_card.set_evidence(
            'Product Registry + Inventory projection · no Collection writes'
        )
        self.authority_card.setAccessibleName(
            'Collection Position Projection. Read-only. Authority gate. '
            'Product Registry and Inventory projection. No Collection writes.'
        )

        self.field_authority_panel = QFrame()
        self.field_authority_panel.setObjectName('collectionPositionFieldAuthority')
        self.field_authority_title_label = QLabel('Unrecorded Collection fields')
        self.field_authority_title_label.setObjectName(
            'collectionPositionFieldAuthorityTitle'
        )
        self.field_authority_detail_label = QLabel(
            'Condition / Grade and Collector Intent remain Not recorded until their '
            'authority is approved. This workspace does not infer or write those values.'
        )
        self.field_authority_detail_label.setObjectName(
            'collectionPositionFieldAuthorityDetail'
        )
        self.field_authority_detail_label.setWordWrap(True)
        self.field_authority_panel.setAccessibleName(
            'Unrecorded Collection fields. Condition / Grade and Collector Intent '
            'remain Not recorded until authority is approved. This workspace does not '
            'infer or write those values.'
        )
        field_authority_layout = QVBoxLayout(self.field_authority_panel)
        field_authority_layout.setContentsMargins(14, 10, 14, 10)
        field_authority_layout.setSpacing(3)
        field_authority_layout.addWidget(self.field_authority_title_label)
        field_authority_layout.addWidget(self.field_authority_detail_label)

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

        self.empty_state_panel = QFrame()
        self.empty_state_panel.setObjectName('collectionPositionEmptyState')
        self.empty_state_title_label = QLabel('No linked Collection positions')
        self.empty_state_title_label.setObjectName('collectionPositionEmptyStateTitle')
        self.empty_state_detail_label = QLabel(
            'This workspace is a read-only Product Registry + Inventory projection. '
            'Collection writes remain blocked until their authority is approved.'
        )
        self.empty_state_detail_label.setObjectName('collectionPositionEmptyStateDetail')
        self.empty_state_detail_label.setWordWrap(True)
        self.empty_state_panel.setAccessibleName(
            'No linked Collection positions. '
            'Read-only Product Registry and Inventory projection. '
            'Collection writes remain blocked until authority is approved.'
        )
        empty_state_layout = QVBoxLayout(self.empty_state_panel)
        empty_state_layout.setContentsMargins(14, 10, 14, 10)
        empty_state_layout.setSpacing(3)
        empty_state_layout.addWidget(self.empty_state_title_label)
        empty_state_layout.addWidget(self.empty_state_detail_label)

        self.results_table = QTableWidget(0, len(self.COLUMN_HEADERS))
        self.results_table.setObjectName('collectionPositionResultsTable')
        self.results_table.setHorizontalHeaderLabels(self.COLUMN_HEADERS)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setStretchLastSection(True)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.authority_card)
        layout.addWidget(self.field_authority_panel)
        layout.addLayout(controls)
        layout.addWidget(self.status_label)
        layout.addWidget(self.empty_state_panel)
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
        self.empty_state_panel.setVisible(not results)
        if query and not results:
            self.status_label.setText('No Collection positions matched this search.')
            self.empty_state_title_label.setText('No matching Collection positions')
            self.empty_state_detail_label.setText(
                'Try another product, product ID, asset ID, or location. '
                'The workspace remains a read-only Product Registry + Inventory projection.'
            )
        elif results:
            self.status_label.setText(f'{len(results)} Collection position(s) found.')
        else:
            self.status_label.setText('No Collection positions are currently linked.')
            self.empty_state_title_label.setText('No linked Collection positions')
            self.empty_state_detail_label.setText(
                'This workspace is a read-only Product Registry + Inventory projection. '
                'Collection writes remain blocked until their authority is approved.'
            )
