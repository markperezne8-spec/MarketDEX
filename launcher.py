import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from services.listing_publication_execution_service import ListingPublicationExecutionService
from ui.main_window import MainWindow
if __name__=='__main__':
 svc=ListingPublicationExecutionService(Path(__file__).parent/'data'/'marketdex.sqlite3')
 app=QApplication(sys.argv); w=MainWindow(svc); w.show(); sys.exit(app.exec())
