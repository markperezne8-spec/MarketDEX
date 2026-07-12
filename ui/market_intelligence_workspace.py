from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from market_intelligence.composition import MarketIntelligenceComposition


class MarketIntelligenceWorkspace(QWidget):
    """Read-only Market Intelligence command-center surface."""

    COLUMN_HEADERS = ('Capability', 'Status', 'Boundary')

    def __init__(self, intelligence: MarketIntelligenceComposition, parent=None):
        super().__init__(parent)
        self.intelligence = intelligence
        self.setObjectName('marketIntelligenceWorkspace')

        title = QLabel('Market Intelligence')
        title.setObjectName('marketIntelligenceTitle')
        subtitle = QLabel(
            'Read-only market signal foundation. Live providers, automation, and mutation authority are intentionally disabled.'
        )
        subtitle.setWordWrap(True)
        subtitle.setObjectName('marketIntelligenceSubtitle')

        self.status_label = QLabel('Market Intelligence readiness not loaded.')
        self.status_label.setObjectName('marketIntelligenceStatusLabel')

        self.results_table = QTableWidget(0, len(self.COLUMN_HEADERS))
        self.results_table.setObjectName('marketIntelligenceReadinessTable')
        self.results_table.setHorizontalHeaderLabels(self.COLUMN_HEADERS)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setStretchLastSection(True)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.status_label)
        layout.addWidget(self.results_table, 1)
        self.refresh_results()

    def refresh_results(self) -> None:
        rows = self._readiness_rows()
        self.results_table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.results_table.setItem(row_index, column_index, item)
        self.status_label.setText(
            'Market Intelligence is mounted in read-only offline mode.'
        )

    def _readiness_rows(self) -> tuple[tuple[str, str, str], ...]:
        return (
            (
                'Observation Gateway',
                f'{len(self.intelligence.observation_gateway.provider_ids)} provider(s) registered',
                'Provider-neutral read boundary; no live network calls.',
            ),
            (
                'Attention Signal Service',
                'Ready',
                'Derives evidence-backed signals only; no automated actions.',
            ),
            (
                'Marketplace Catalog',
                f'{len(self.intelligence.marketplace_registry.definitions)} marketplace(s)',
                'Static capability registry; no credential access.',
            ),
            (
                'Mode Catalog',
                f'{len(self.intelligence.mode_catalog.definitions)} mode(s)',
                'Business and collector categories only.',
            ),
            (
                'Visualization Catalog',
                f'{len(self.intelligence.visualization_catalog.definitions)} definition(s)',
                'Catalog definitions only; no charts rendered in this slice.',
            ),
        )
