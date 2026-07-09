from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QMainWindow,
    QStackedWidget,
    QHBoxLayout,
    QWidget,
)


MODULES = (
    "Mission Control",
    "Inventory",
    "Collection",
    "Attention Queue",
    "Capital Deployment",
    "Population Intelligence",
    "Product Contents",
    "Platforms",
    "Market Calendar",
    "Product Registry",
    "Grading",
    "Decisions",
    "Data Quality",
    "Ops Contract",
    "Enter Once",
    "Exceptions",
    "Audit Trail",
    "Desktop Map",
    "Settlement",
    "Allocation",
)


class MainWindow(QMainWindow):
    def __init__(self, app_version: str, specification_build: str) -> None:
        super().__init__()
        self.setWindowTitle(f"MarketDEX OS {app_version}")
        self.resize(1200, 760)

        navigation = QListWidget()
        pages = QStackedWidget()

        for module_name in MODULES:
            navigation.addItem(module_name)
            label = QLabel(f"{module_name}\n\nImplementation pending specification-traced vertical slice.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pages.addWidget(label)

        navigation.currentRowChanged.connect(pages.setCurrentIndex)
        navigation.setCurrentRow(0)

        layout = QHBoxLayout()
        layout.addWidget(navigation, 1)
        layout.addWidget(pages, 4)

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.statusBar().showMessage(
            f"Desktop {app_version} | Business Specification Build {specification_build}"
        )
