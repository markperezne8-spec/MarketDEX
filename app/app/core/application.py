import sys
import traceback
from PySide6.QtWidgets import QApplication

def run():
    try:
        print("Loading startup...")
        from app.core.startup import startup
        startup()
        print("Startup OK")

        print("Creating QApplication...")
        app = QApplication(sys.argv)

        print("Loading AppShell...")
        from app.ui.app_shell.app_shell import AppShell
        window = AppShell()

        print("Showing window...")
        window.show()

        sys.exit(app.exec())

    except Exception:
        print("\n=== MARKETDEX STARTUP ERROR ===")
        traceback.print_exc()
        input("\nPress Enter to close...")
