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
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from reports.definitions import ReportCatalog
from reports.inventory_age_query import InventoryAgeReportQueryResult
from reports.inventory_turnover_presentation import InventoryTurnoverPresentation
from reports.purchase_source_performance_contract import PurchaseSourcePerformanceRequest
from reports.purchase_source_performance_presentation import present_purchase_source_performance
from reports.purchase_source_performance_query import PurchaseSourcePerformanceQueryResponse
from reports.purchase_source_performance_presentation import (
    PurchaseSourcePerformancePresentation,
    PurchaseSourcePerformancePresentationRow,
)


def _unavailable_turnover_presentation() -> InventoryTurnoverPresentation:
    return InventoryTurnoverPresentation(
        outcome='unavailable',
        status='UNAVAILABLE',
        reason='Presentation snapshot not provided',
        period='Unavailable',
        formula='Unavailable',
        evidence='unavailable',
        opening_units='Unavailable',
        closing_units='Unavailable',
        average_units='Unavailable',
        completed_sale_units='Unavailable',
        turnover_ratio='Unavailable',
        turnover_percentage='Unavailable',
    )


def _unavailable_purchase_source_presentation() -> PurchaseSourcePerformancePresentation:
    return PurchaseSourcePerformancePresentation(
        period_start=date(1970, 1, 1),
        period_end=date(1970, 1, 2),
        as_of=date(1970, 1, 2),
        source_coverage=('unavailable',),
        provenance=('reports-workspace:preview-unavailable',),
        rows=(
            PurchaseSourcePerformancePresentationRow(
                purchase_source_label='Unavailable',
                outcome='unavailable',
                acquired_units=None,
                completed_sale_units=None,
                remaining_unsold_units=None,
                sell_through_percentage=None,
                evidence_state='unavailable',
                reason='Presentation snapshot not provided',
                provenance=('reports-workspace:preview-unavailable',),
            ),
        ),
    )


class ReportsWorkspace(QWidget):
    """Read-only Reports catalog and result surface."""

    HEADERS = ('Report', 'Business Question', 'Evidence', 'Status')
    TURNOVER_METRICS = (
        ('Turnover', 'turnover_percentage', 'reportsTurnoverPercentage'),
        ('Ratio', 'turnover_ratio', 'reportsTurnoverRatio'),
        ('Opening units', 'opening_units', 'reportsTurnoverOpeningUnits'),
        ('Closing units', 'closing_units', 'reportsTurnoverClosingUnits'),
        ('Completed sales', 'completed_sale_units', 'reportsTurnoverCompletedSales'),
        ('Average units', 'average_units', 'reportsTurnoverAverageUnits'),
    )

    def __init__(
        self,
        catalog: ReportCatalog,
        query_report: Callable[[str, str, date], InventoryAgeReportQueryResult]
        | None = None,
        parent=None,
        *,
        turnover_presentation: InventoryTurnoverPresentation | None = None,
        purchase_source_presentation: PurchaseSourcePerformancePresentation | None = None,
        purchase_source_query: Callable[[PurchaseSourcePerformanceRequest], PurchaseSourcePerformanceQueryResponse]
        | None = None,
    ):
        super().__init__(parent)
        self.catalog = catalog
        self.query_report = query_report
        self.purchase_source_query = purchase_source_query
        self.turnover_presentation = (
            turnover_presentation or _unavailable_turnover_presentation()
        )
        self.purchase_source_presentation = (
            purchase_source_presentation or _unavailable_purchase_source_presentation()
        )
        self.setObjectName('reportsWorkspace')

        title = QLabel('Reports')
        title.setObjectName('reportsTitle')

        subtitle = QLabel(
            'Read-only report catalog. Purchase Source Performance uses the composition-owned '
            'query boundary; no persistence, exports, or background execution are enabled.'
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
        self.report_table.setSelectionMode(QTableWidget.SingleSelection)
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.report_table.horizontalHeader().setStretchLastSection(True)
        self.report_table.setMinimumHeight(120)
        self.report_table.setMaximumHeight(150)

        self.turnover_panel = QGroupBox('Inventory Turnover')
        self.turnover_panel.setObjectName('reportsInventoryTurnoverPanel')
        self.turnover_panel.setMinimumHeight(350)

        self.turnover_status_label = QLabel(
            'Read-only visual preview · '
            f'{self.turnover_presentation.status} · '
            f'{self.turnover_presentation.reason}'
        )
        self.turnover_status_label.setObjectName('reportsInventoryTurnoverStatus')
        self.turnover_status_label.setWordWrap(True)

        self.turnover_metric_labels: dict[str, QLabel] = {}
        self.turnover_metric_cards: dict[str, QFrame] = {}
        metrics_layout = QGridLayout()
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setHorizontalSpacing(10)
        metrics_layout.setVerticalSpacing(10)
        for index, (caption, field_name, object_name) in enumerate(self.TURNOVER_METRICS):
            card = QFrame()
            card.setObjectName(f'{object_name}Card')
            card.setFrameShape(QFrame.StyledPanel)
            card.setMinimumHeight(76)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 9, 12, 9)
            card_layout.setSpacing(2)

            caption_label = QLabel(caption.upper())
            caption_label.setObjectName(f'{object_name}Caption')
            caption_label.setMinimumHeight(18)
            value_label = QLabel(str(getattr(self.turnover_presentation, field_name)))
            value_label.setObjectName(object_name)
            value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            value_label.setMinimumHeight(26)

            card_layout.addWidget(caption_label)
            card_layout.addWidget(value_label)
            metrics_layout.addWidget(card, index // 3, index % 3)
            self.turnover_metric_cards[object_name] = card
            self.turnover_metric_labels[object_name] = value_label

        self.turnover_period_label = QLabel(
            f'PERIOD  ·  {self.turnover_presentation.period}  ·  '
            f'{self.turnover_presentation.status}'
        )
        self.turnover_period_label.setObjectName('reportsTurnoverPeriod')
        self.turnover_formula_label = QLabel(
            f'FORMULA  ·  {self.turnover_presentation.formula}'
        )
        self.turnover_formula_label.setObjectName('reportsTurnoverFormula')
        self.turnover_evidence_label = QLabel(
            f'EVIDENCE  ·  {self.turnover_presentation.evidence}  ·  no mutation authority'
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

        self.purchase_source_panel = QGroupBox('Purchase Source Performance')
        self.purchase_source_panel.setObjectName('reportsPurchaseSourcePanel')
        self.purchase_source_panel.setMinimumHeight(220)
        self.purchase_source_status_label = QLabel()
        self.purchase_source_status_label.setObjectName('reportsPurchaseSourceStatus')
        self.purchase_source_status_label.setWordWrap(True)
        self.purchase_source_table = QTableWidget(0, 5)
        self.purchase_source_table.setObjectName('reportsPurchaseSourceTable')
        self.purchase_source_table.setHorizontalHeaderLabels(
            ('Purchase source', 'Outcome', 'Acquired', 'Completed sales', 'Sell-through')
        )
        self.purchase_source_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.purchase_source_table.setSelectionMode(QTableWidget.NoSelection)
        self.purchase_source_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.purchase_source_table.horizontalHeader().setStretchLastSection(True)
        self.purchase_source_table.setMinimumHeight(92)
        purchase_source_layout = QVBoxLayout(self.purchase_source_panel)
        purchase_source_layout.setContentsMargins(12, 12, 12, 12)
        purchase_source_layout.setSpacing(8)
        self.purchase_source_period_start_input = QDateEdit(QDate(2026, 1, 1))
        self.purchase_source_period_start_input.setObjectName('reportsPurchaseSourcePeriodStart')
        self.purchase_source_period_start_input.setCalendarPopup(True)
        self.purchase_source_period_start_input.setDisplayFormat('yyyy-MM-dd')

        self.purchase_source_period_end_input = QDateEdit(QDate(2026, 2, 1))
        self.purchase_source_period_end_input.setObjectName('reportsPurchaseSourcePeriodEnd')
        self.purchase_source_period_end_input.setCalendarPopup(True)
        self.purchase_source_period_end_input.setDisplayFormat('yyyy-MM-dd')

        self.purchase_source_as_of_input = QDateEdit(QDate(2026, 2, 1))
        self.purchase_source_as_of_input.setObjectName('reportsPurchaseSourceAsOf')
        self.purchase_source_as_of_input.setCalendarPopup(True)
        self.purchase_source_as_of_input.setDisplayFormat('yyyy-MM-dd')

        self.purchase_source_run_button = QPushButton('Run read-only report')
        self.purchase_source_run_button.setObjectName('reportsPurchaseSourceRunButton')
        self.purchase_source_run_button.clicked.connect(self.run_purchase_source_performance)

        purchase_source_controls = QWidget()
        purchase_source_controls.setObjectName('reportsPurchaseSourceControls')
        purchase_source_form = QFormLayout(purchase_source_controls)
        purchase_source_form.setContentsMargins(0, 0, 0, 0)
        purchase_source_form.setVerticalSpacing(8)
        purchase_source_form.addRow('Period start', self.purchase_source_period_start_input)
        purchase_source_form.addRow('Period end', self.purchase_source_period_end_input)
        purchase_source_form.addRow('As-of date', self.purchase_source_as_of_input)
        purchase_source_form.addRow('', self.purchase_source_run_button)
        purchase_source_layout.addWidget(self.purchase_source_status_label)
        purchase_source_layout.addWidget(purchase_source_controls)
        purchase_source_layout.addWidget(self.purchase_source_table)
        self._refresh_purchase_source_preview()

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

        self.query_form_widget = QWidget()
        self.query_form_widget.setObjectName('reportsInventoryAgeQueryForm')
        query_form = QFormLayout(self.query_form_widget)
        query_form.setContentsMargins(0, 0, 0, 0)
        query_form.setVerticalSpacing(10)
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
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.setMinimumHeight(180)

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName('reportsScrollContent')
        content_layout = QVBoxLayout(self.scroll_content)
        content_layout.setContentsMargins(18, 18, 18, 18)
        content_layout.setSpacing(10)
        content_layout.addWidget(title)
        content_layout.addWidget(subtitle)
        content_layout.addWidget(self.status_label)
        content_layout.addWidget(self.report_table)
        content_layout.addWidget(self.turnover_panel)
        content_layout.addWidget(self.purchase_source_panel)
        content_layout.addWidget(self.query_form_widget)
        content_layout.addWidget(self.result_status_label)
        content_layout.addWidget(self.result_table)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName('reportsScrollArea')
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidget(self.scroll_content)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll_area)

        self.refresh()


    def _refresh_purchase_source_preview(self) -> None:
        presentation = self.purchase_source_presentation
        self.purchase_source_status_label.setText(
            'Read-only result · '
            f'{len(presentation.rows)} source row(s) · '
            f'PERIOD {presentation.period_start.isoformat()} → {presentation.period_end.isoformat()} · '
            f'AS-OF {presentation.as_of.isoformat()} · '
            f'COVERAGE {", ".join(presentation.source_coverage)}'
        )
        self.purchase_source_table.setRowCount(len(presentation.rows))
        for row_index, row in enumerate(presentation.rows):
            values = (
                row.purchase_source_label,
                row.outcome.upper(),
                row.acquired_units if row.acquired_units is not None else 'Unavailable',
                row.completed_sale_units if row.completed_sale_units is not None else 'Unavailable',
                (f'{row.sell_through_percentage}%' if row.sell_through_percentage is not None else 'Unavailable'),
            )
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.purchase_source_table.setItem(row_index, column_index, item)
        self.purchase_source_table.resizeRowsToContents()

    def run_purchase_source_performance(self) -> None:
        if self.purchase_source_query is None:
            self.purchase_source_status_label.setText(
                'Purchase Source Performance: query execution remains composition-owned.'
            )
            return

        period_start = self.purchase_source_period_start_input.date().toPython()
        period_end = self.purchase_source_period_end_input.date().toPython()
        as_of = self.purchase_source_as_of_input.date().toPython()
        try:
            request = PurchaseSourcePerformanceRequest(
                period_start=period_start,
                period_end=period_end,
                as_of=as_of,
                source_coverage_required=('inventory', 'sale_completion'),
            )
            response = self.purchase_source_query(request)
            self.purchase_source_presentation = present_purchase_source_performance(response)
        except (TypeError, ValueError) as exc:
            self.purchase_source_status_label.setText(
                f'Purchase Source Performance: INVALID REQUEST · {exc}'
            )
            return
        except Exception:
            self.purchase_source_presentation = _unavailable_purchase_source_presentation()
            self.purchase_source_status_label.setText(
                'Purchase Source Performance: UNAVAILABLE · query boundary unavailable'
            )
        self._refresh_purchase_source_preview()

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
            'read-only query execution remains composition-owned.'
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
                    ('As-of date', as_of_date.isoformat() if as_of_date else 'Not provided'),
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
