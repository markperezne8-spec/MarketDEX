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

from reports.definitions import ReportCatalog


class ReportsWorkspace(QWidget):
    """Read-only catalog surface for approved Reports definitions."""

    HEADERS = ('Report', 'Business Question', 'Evidence', 'Status')

    def __init__(self, catalog: ReportCatalog, parent=None):
        super().__init__(parent)
        self.catalog = catalog
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.status_label)
        layout.addWidget(self.report_table, 1)

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
        self.report_table.resizeRowsToContents()
        self.status_label.setText(
            f'{len(definitions)} approved report definition(s) · catalog only · '
            'query execution remains composition-owned.'
        )
