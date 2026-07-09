from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from app.config import load_config
from app.logging_config import configure_logging
from database.database_manager import DatabaseManager
from ui.main_window import MainWindow


def run() -> int:
    config = load_config()
    logger = configure_logging(config.log_dir)
    logger.info("Starting %s %s", config.app_name, config.app_version)

    application = QApplication(sys.argv)

    try:
        database = DatabaseManager(config.database_path)
        database.initialize()
        logger.info("Database initialized at %s", config.database_path)

        window = MainWindow(config.app_version, config.specification_build)
        window.show()
        exit_code = application.exec()
        logger.info("Application shutdown with exit code %s", exit_code)
        return exit_code
    except Exception:
        logger.exception("Fatal application startup failure")
        QMessageBox.critical(
            None,
            "MarketDEX OS Startup Error",
            "MarketDEX OS could not start. Review desktop/logs/marketdex.log for details.",
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
