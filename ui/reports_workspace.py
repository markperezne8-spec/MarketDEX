from __future__ import annotations

from datetime import date
from typing import Callable

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDateEdit,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from reports.definitions import ReportCatalog
from reports.inventory_age_query import InventoryAgeReportQueryResult


class ReportsWorkspace(QWidget):
    """Read-only Reports catalog and result surface."""

    HEADERS = ('Report', 'Business Question', 'Evidence', 'Status')
    TURNOVER_METRICS = (
        ('Turnover', '50.0%', 'reportsTurnoverPercentage'),
        ('Ratio', '0.5×', 'reportsTurnoverRatio'),
        ('Opening units', '10', 'reportsTurnoverOpeningUnits'),
        ('Closing units', '6', 'reportsTurnoverClosingUnits'),
        ('Completed sales', '4', 'reportsTurnoverCompletedSales'),
        ('Average units', '8', 'reportsTurnoverAverageUnits'),
    )

    def __init__(
        self,
        catalog: ReportCatalog,
        query_report: Callable[[str, str, date], InventoryAgeReportQueryResult]
        | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.catalog = catalog
        self.query_report = query_report
        self.setObjectName('reportsWorkspace')

        title = QLabel('Reports')
        title.setObjectName('reportsTitle')

        subtitle = QLabel(
            'Read-only report catalog. Approved Reports use the offline composition boundary; '
            'no live providers, persistence, or automatic execution are enabled.'
        )
        subtitle.setObjectName('reportsSubtitle')
        subtitle.setWordWrap(True)

        self.status_label = QLabel()
        self.status_label.setObjectName('reportsStatusLabel')

        self.report_table = QTableWidget(0, len(self.HEADERS))
        self.report_table.setObjectName('reportsCatalogTable')
        self.report_table.setHorizontalHeaderLabels(self.HEADERS)
        self.report_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.report_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.report_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.report_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.report_table.horizontalHeader().setStretchLastSection(True)
        self.report_table.setMaximumHeight(190)

        self.turnover_panel = QGroupBox('Inventory Turnover')
        self.turnover_panel.setObjectName('reportsInventoryTurnoverPanel')

        self.turnover_status_label = QLabel(
            'Read-only visual preview · deterministic CAP-012H result shape · no live execution.'
        )
        self.turnover_status_label.setObjectName('reportsInventoryTurnoverStatus')
        self.turnover_status_label.setWordWrap(True)

        self.turnover_metric_labels: dict[str, QLabel] = {}
        metrics_layout = QGridLayout()
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setHorizontalSpacing(10)
        metrics_layout.setVerticalSpacing(10)
        for index, (caption, value, object_name) in enumerate(self.TURNOVER_METRICS):
            card = QFrame()
            card.setObjectName(f'{object_name}Card')
            card.setFrameShape(QFrame.StyledPanel)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 9, 12, 9)
            card_layout.setSpacing(2)

            caption_label = QLabel(caption.upper())
            caption_label.setObjectName(f'{object_name}Caption')
            value_label = QLabel(value)
            value_label.setObjectName(object_name)
            value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            card_layout.addWidget(caption_label)
            card_layout.addWidget(value_label)
            metrics_layout.addWidget(card, index // 3, index % 3)
            self.turnover_metric_labels[object_name] = value_label

        self.turnover_period_label = QLabel('PERIOD  ·  2026-01-01 → 2026-02-01  ·  CLOSED')
        self.turnover_period_label.setObjectName('reportsTurnoverPeriod')
        self.turnover_formula_label = QLabel('FORMULA  ·  inventory-turnover-units-v1')
        self.turnover_formula_label.setObjectName('reportsTurnoverFormula')
        self.turnover_evidence_label = QLabel(
            'EVIDENCE AVAILABLE  ·  deterministic read-only sample  ·  no mutation authority'
        )
        self.turnover_evidence_label.setObjectName('reportsTurnoverEvidence')
        self.turnover_evidence_label.setWordWrap(True)
        self.turnover_guardrail_label = QLabel(
            'Unavailable evidence exposes no turnover values. Conflicting evidence blocks numeric output.'
        )
        self.turnover_guardrail_label.setObjectName('reportsTurnoverGuardrails')
        self.turnover_guardrail_label.setWordWrap(True)

        turnover_layout = QVBoxLayout(self.turnover_panel)
        turnover_layout.setContentsMargins(12, 12, 12, 12)
        turnover_layout.setSpacing(8)
        turnover_layout.addWidget(self.turnover_status_label)
        turnover_layout.addLayout(metrics_layout)
        turnover_layout.addWidget(self.turnover_period_label)
        turnover_layout.addWidget(self.turnover_formula_label)
        turnover_layout.addWidget(self.turnover_evidence_label)
        turnover_layout.addWidget(self.turnover_guardrail_label)

        self.inventory_position_input = QLineEdit()
        self.inventory_position_input.setObjectName('reportsInventoryPositionInput')
        self.inventory_position_input.setPlaceholderText('Inventory position ID')

        self.as_of_date_input = QDateEdit(QDate.currentDate())
        self.as_of_date_input.setObjectName('reportsAsOfDateInput')
        self.as_of_date_input.setCalendarPopup(True)
        self.as_of_date_input.setDisplayFormat('yyyy-MM-dd')

        self.review_button = QPushButton('Review Result')
        self.review_button.setObjectName('reportsReviewResultButton')
        self.review_button.clicked.connect(self.review_selected_report)

        query_form = QFormLayout()
        query_form.addRow('Inventory position', self.inventory_position_input)
        query_form.addRow('As-of date', self.as_of_date_input)
        query_form.addRow('', self.review_button)

        self.result_status_label = QLabel()
        self.result_status_label.setObjectName('reportsResultStatusLabel')
        self.result_status_label.setWordWrap(True)

        self.result_table = QTableWidget(0, 2)
        self.result_table.setObjectName('reportsResultTable')
        self.result_table.setHorizontalHeaderLabels(('Field', 'Value'))
        self.result_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.result_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.setMinimumHeight(260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.status_label)
        layout.addWidget(self.report_table, 1)
        layout.addWidget(self.turnover_panel)
        layout.addLayout(query_form)
        layout.addWidget(self.result_status_label)
        layout.addWidget(self.result_table)

        self.refresh()

    def refresh(self) -> None:
        definitions = self.catalog.list_definitions()
        self.report_table.setRowCount(len(definitions))
        for row_index, definition in enumerate(definitions):
            values = (
                definition.name,
                definition.business_question,
                ', '.join(definition.evidence_families),
                'APPROVED · READ-ONLY',
            )
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.report_table.setItem(row_index, column_index, item)
        if definitions:
            self.report_table.selectRow(0)
        self.report_table.resizeRowsToContents()
        self.status_label.setText(
            f'{len(definitions)} approved report definition(s) · catalog only · '
            'query execution remains composition-owned.'
        )
        self.result_status_label.setText(
            'Enter an inventory position and select an as-of date to review a read-only result.'
        )
        self.result_table.setRowCount(0)

    def review_selected_report(self) -> None:
        if self.query_report is None:
            self.result_status_label.setText(
                'Query execution remains composition-owned by the application.'
            )
            return

        row_index = self.report_table.currentRow()
        definitions = self.catalog.list_definitions()
        if row_index < 0 or row_index >= len(definitions):
            self.result_status_label.setText('Select an approved report definition first.')
            return
        if definitions[row_index].report_id != 'inventory-age-patterns':
            self.result_status_label.setText(
                f'{definitions[row_index].name}: visible read-only preview only; '
                'interactive query execution is not enabled for this report.'
            )
            return

        inventory_position_id = self.inventory_position_input.text().strip()
        if not inventory_position_id:
            self.result_status_label.setText(
                'Enter an inventory position ID before reviewing a result.'
            )
            return

        report_name = definitions[row_index].name
        result = self.query_report(
            definitions[row_index].report_id,
            inventory_position_id,
            self.as_of_date_input.date().toPython(),
        )
        self._render_result(
            result,
            report_name,
            inventory_position_id,
            self.as_of_date_input.date().toPython(),
        )

    def _render_result(
        self,
        result: InventoryAgeReportQueryResult,
        report_name: str,
        inventory_position_id: str = '',
        as_of_date: date | None = None,
    ) -> None:
        self.result_table.setRowCount(0)
        if not result.is_found or result.row is None:
            self.result_status_label.setText(
                f'{report_name}: CATALOG-ONLY · {result.outcome.upper()} · '
                f'{result.reason or "No report row available"}'
            )
            self._set_result_rows(
                (
                    ('Outcome', result.outcome.upper()),
                    ('Reason', result.reason or 'No report row available'),
                    ('Evidence state', 'unavailable'),
                    ('Evidence reason', result.reason or 'No report row available'),
                    ('Inventory position', inventory_position_id or 'Not provided'),
                    (
                        'As-of date',
                        as_of_date.isoformat() if as_of_date is not None else 'Not provided',
                    ),
                    ('Age (days)', 'unavailable'),
                    ('Age reason', result.reason or 'No report row available'),
                    ('Source domain', 'inventory'),
                    ('Source date', 'unavailable · no Inventory detail evidence'),
                    ('Source field', 'purchase_date'),
                )
            )
            return

        row = result.row
        self.result_status_label.setText(
            f'{report_name}: FOUND · CATALOG-ONLY · READ-ONLY EVIDENCE'
        )
        self._set_result_rows(
            (
                ('Product', row.product_name),
                ('Inventory position', row.inventory_position_id),
                ('Quantity', row.current_quantity),
                ('Inventory status', row.inventory_status),
                ('Storage location', row.storage_location or 'Not recorded'),
                ('As-of date', row.as_of_date.isoformat()),
                ('Evidence', f'{row.evidence_state} · {row.evidence_reason}'),
                ('Evidence state', row.evidence_state),
                ('Evidence reason', row.evidence_reason),
                ('Source domain', row.source_domain),
                ('Age (days)', row.age_days),
                ('Age reason', row.evidence_reason),
                ('Source date', row.source_start_date.isoformat()),
                ('Source field', 'purchase_date'),
            )
        )

    def _set_result_rows(self, values: tuple[tuple[str, object], ...]) -> None:
        self.result_table.setRowCount(len(values))
        for row_index, (field, value) in enumerate(values):
            for column_index, item_value in enumerate((field, str(value))):
                item = QTableWidgetItem(item_value)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.result_table.setItem(row_index, column_index, item)
        self.result_table.resizeRowsToContents()
