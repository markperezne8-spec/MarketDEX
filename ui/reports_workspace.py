from __future__ import annotations

from datetime import date
from typing import Callable

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDateEdit,
    QFormLayout,
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
    """Read-only Reports catalog and Inventory Age result surface."""

    HEADERS = ('Report', 'Business Question', 'Evidence', 'Status')

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

        self.inventory_position_input = QLineEdit()
        self.inventory_position_input.setObjectName('reportsInventoryPositionInput')
        self.inventory_position_input.setPlaceholderText(
            'Inventory position ID'
        )

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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.status_label)
        layout.addWidget(self.report_table, 1)
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
                    ('Inventory position', inventory_position_id or 'Not provided'),
                    (
                        'As-of date',
                        as_of_date.isoformat() if as_of_date is not None else 'Not provided',
                    ),
                    ('Source domain', 'inventory'),
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
                ('Source domain', row.source_domain),
                ('Age (days)', row.age_days),
                ('Source date', row.source_start_date.isoformat()),
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