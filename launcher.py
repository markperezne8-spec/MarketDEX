import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from services.product_registry_service import ProductRegistryService
from ui.main_window import MainWindow
if __name__=='__main__':
    svc=ProductRegistryService(Path(__file__).parent/'data'/'marketdex.sqlite3')
    app=QApplication(sys.argv); w=MainWindow(svc); w.show(); sys.exit(app.exec())
