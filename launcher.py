import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from composition import ApplicationComposition
from core.runtime_database_migration import migrate_legacy_database_if_needed
from ui.main_window import MainWindow

APP_NAME = 'MarketDEX'
DATABASE_FILENAME = 'marketdex.sqlite3'


def source_root() -> Path:
    return Path(__file__).resolve().parent


def application_data_dir() -> Path:
    override = os.environ.get('MARKETDEX_DATA_DIR')
    if override:
        return Path(override).expanduser().resolve()
    if getattr(sys, 'frozen', False):
        local_app_data = os.environ.get('LOCALAPPDATA')
        if local_app_data:
            return Path(local_app_data) / APP_NAME
        return Path.home() / 'AppData' / 'Local' / APP_NAME
    return source_root() / 'runtime'


def runtime_database_path() -> Path:
    runtime_dir = application_data_dir()
    runtime_dir.mkdir(parents=True, exist_ok=True)
    return runtime_dir / DATABASE_FILENAME


def build_application(database_path: Path) -> ApplicationComposition:
    return ApplicationComposition(database_path)


def build_main_window(database_path: Path) -> MainWindow:
    return build_application(database_path).build_main_window()


def initialize_runtime() -> Path:
    database_path = runtime_database_path()
    migrate_legacy_database_if_needed(database_path, source_root())
    build_application(database_path)
    return database_path


def main(argv=None) -> int:
    arguments = list(sys.argv if argv is None else argv)
    database_path = runtime_database_path()
    migrate_legacy_database_if_needed(database_path, source_root())
    composition = build_application(database_path)
    if '--verify-runtime' in arguments:
        composition.verify_runtime()
        print(f'MarketDEX runtime verified: {database_path}')
        return 0
    app = QApplication(arguments)
    window = composition.build_main_window()
    window.showMaximized()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
