from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from market_intelligence.composition import MarketIntelligenceComposition
from market_intelligence.observations import ObservationKind
from market_intelligence.offline_fixtures import OFFLINE_SAMPLE_PRODUCT_ID, OFFLINE_SAMPLE_SOURCE_ID


class MarketIntelligenceWorkspace(QWidget):
    """Read-only Market Intelligence command-center surface."""

    READINESS_HEADERS = ('Capability', 'Status', 'Boundary')
    QUERY_HEADERS = ('Query ID', 'Name', 'Products', 'Marketplaces', 'Observations', 'Notes')
    EVIDENCE_HEADERS = ('Evidence', 'Value', 'Confidence', 'Sample', 'Observed')
    SIGNAL_HEADERS = ('Signal', 'Severity', 'Action', 'Evidence')

    def __init__(self, intelligence: MarketIntelligenceComposition, parent=None):
        super().__init__(parent)
        self.intelligence = intelligence
        self.setObjectName('marketIntelligenceWorkspace')

        title = QLabel('Market Intelligence')
        title.setObjectName('marketIntelligenceTitle')
        subtitle = QLabel(
            'Read-only offline sample evidence. Live providers, automation, and mutation authority are intentionally disabled.'
        )
        subtitle.setWordWrap(True)
        subtitle.setObjectName('marketIntelligenceSubtitle')

        self.status_label = QLabel('Market Intelligence readiness not loaded.')
        self.status_label.setObjectName('marketIntelligenceStatusLabel')

        self.readiness_table = self._table(self.READINESS_HEADERS, 'marketIntelligenceReadinessTable')
        self.query_table = self._table(self.QUERY_HEADERS, 'marketIntelligenceResearchQueryTable')
        self.evidence_table = self._table(self.EVIDENCE_HEADERS, 'marketIntelligenceEvidenceTable')
        self.signal_table = self._table(self.SIGNAL_HEADERS, 'marketIntelligenceSignalTable')

        query_title = QLabel('Saved research queries · read-only')
        query_title.setObjectName('marketIntelligenceResearchQueryTitle')
        self.query_status = QLabel('Research query catalog not loaded.')
        self.query_status.setWordWrap(True)
        self.query_status.setObjectName('marketIntelligenceResearchQueryStatus')

        evidence_title = QLabel('Offline sample evidence · Mega Evolution ETB')
        evidence_title.setObjectName('marketIntelligenceEvidenceTitle')
        signal_title = QLabel('Derived attention signals · read-only')
        signal_title.setObjectName('marketIntelligenceSignalTitle')
        visualization_title = QLabel('Offline visualization · relative evidence view')
        visualization_title.setObjectName('marketIntelligenceVisualizationTitle')
        self.visualization_status = QLabel('Catalog definition: Daily Market Volume · fixture evidence only')
        self.visualization_status.setObjectName('marketIntelligenceVisualizationStatus')

        self.price_bar = self._bar('Observed price · USD 89.99')
        self.volume_bar = self._bar('Daily volume · 25 samples')
        visualization_layout = QVBoxLayout()
        visualization_layout.addWidget(visualization_title)
        visualization_layout.addWidget(self.visualization_status)
        visualization_layout.addLayout(self._bar_row('Market price', self.price_bar))
        visualization_layout.addLayout(self._bar_row('Daily volume', self.volume_bar))

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.status_label)
        layout.addWidget(self.readiness_table, 2)
        layout.addWidget(query_title)
        layout.addWidget(self.query_status)
        layout.addWidget(self.query_table, 1)
        layout.addWidget(evidence_title)
        layout.addWidget(self.evidence_table, 2)
        layout.addWidget(signal_title)
        layout.addWidget(self.signal_table, 1)
        layout.addLayout(visualization_layout)

        self.refresh_results()

    def _table(self, headers: tuple[str, ...], object_name: str) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setObjectName(object_name)
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.horizontalHeader().setStretchLastSection(True)
        return table

    def _bar(self, text: str) -> QProgressBar:
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(0)
        bar.setFormat(text)
        bar.setTextVisible(True)
        bar.setObjectName('marketIntelligenceEvidenceBar')
        return bar

    def _bar_row(self, label: str, bar: QProgressBar) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addWidget(QLabel(label))
        row.addWidget(bar, 1)
        return row

    def refresh_results(self) -> None:
        self._set_rows(self.readiness_table, self.READINESS_HEADERS, self._readiness_rows())
        self._refresh_query_rows()
        observations = self.intelligence.observation_gateway.list_observations(
            OFFLINE_SAMPLE_SOURCE_ID,
            OFFLINE_SAMPLE_PRODUCT_ID,
        )
        evidence_rows = tuple(
            (
                observation.metadata.get('label', observation.kind.value),
                self._format_value(observation),
                f'{observation.confidence:.0%}',
                str(observation.sample_size or '—'),
                observation.observed_at.strftime('%Y-%m-%d %H:%M UTC'),
            )
            for observation in observations
        )
        self._set_rows(self.evidence_table, self.EVIDENCE_HEADERS, evidence_rows)
        signals = self.intelligence.attention_signal_service.derive_signals(observations)
        signal_rows = tuple(
            (
                signal.title,
                signal.severity.name.title(),
                signal.suggested_action.value.title(),
                ', '.join(signal.evidence_ids),
            )
            for signal in signals
        )
        self._set_rows(self.signal_table, self.SIGNAL_HEADERS, signal_rows)
        price = next(item for item in observations if item.kind is ObservationKind.MARKET_PRICE)
        volume = next(item for item in observations if item.kind is ObservationKind.DAILY_VOLUME)
        self.price_bar.setValue(min(100, int(price.value)))
        self.price_bar.setFormat(f'USD {price.value} · offline sample')
        self.volume_bar.setValue(min(100, int(volume.value * 4)))
        self.volume_bar.setFormat(f'{volume.value} daily volume · offline sample')
        self.status_label.setText(
            'Market Intelligence is mounted in read-only offline mode · fixture evidence only.'
        )

    def _refresh_query_rows(self) -> None:
        definitions = self.intelligence.research_query_catalog.list_definitions()
        query_rows = tuple(
            (
                definition.query_id,
                definition.name,
                ', '.join(definition.product_ids) or '—',
                ', '.join(definition.marketplace_ids) or 'All',
                ', '.join(definition.observation_kinds) or 'All',
                definition.notes or '—',
            )
            for definition in definitions
        )
        self._set_rows(self.query_table, self.QUERY_HEADERS, query_rows)
        if definitions:
            self.query_status.setText(
                f'{len(definitions)} saved research query definition(s) · in-memory only · not persisted · not executable.'
            )
        else:
            self.query_status.setText(
                'No saved research queries registered · in-memory only · not persisted · not executable.'
            )

    def _set_rows(
        self,
        table: QTableWidget,
        headers: tuple[str, ...],
        rows: tuple[tuple[str, ...], ...],
    ) -> None:
        table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row_index, column_index, item)

    def _format_value(self, observation) -> str:
        if observation.kind is ObservationKind.MARKET_PRICE:
            return f'{observation.currency or ""} {observation.value}'
        return f'{observation.value}'

    def _readiness_rows(self) -> tuple[tuple[str, str, str], ...]:
        return (
            (
                'Observation Gateway',
                f'{len(self.intelligence.observation_gateway.provider_ids)} provider(s) registered',
                'Provider-neutral read boundary; fixture only, no live network calls.',
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
                'Catalog-backed read-only visualization; no persistent valuation.',
            ),
            (
                'Research Query Catalog',
                f'{len(self.intelligence.research_query_catalog.query_ids)} saved query definition(s)',
                'Composition-owned in-memory definitions; no persistence or execution.',
            ),
        )
