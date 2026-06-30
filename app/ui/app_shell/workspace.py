from PySide6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Slot

from app.ui.pages.mission_control import MissionControlPage
from app.ui.pages.asset_manager_page import AssetManagerPage
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.inventory_page import InventoryPage
from app.ui.pages.settings_page import SettingsPage


class Workspace(QStackedWidget):
    """
    Page container for the application.
    
    Loads and manages all pages accessible from sidebar navigation.
    Routes page requests by identifier string.
    """

    def __init__(self):
        super().__init__()
        
        # Map page identifiers to their widgets
        self.pages_map = {}
        
        # Define pages for sidebar navigation
        # Page identifiers (keys) are used for routing throughout the app
        sidebar_pages = {
            'mission_control': MissionControlPage(),
            'collections': self._create_placeholder('Collections'),
            'business': AssetManagerPage(),
            'intelligence': self._create_placeholder('Intelligence'),
            'system': SettingsPage(),
        }
        
        # Add pages to stack and register in map
        for page_id, page_widget in sidebar_pages.items():
            idx = self.addWidget(page_widget)
            self.pages_map[page_id] = page_widget
        
        # Additional pages (not accessible from sidebar)
        # Can be used programmatically by the application
        additional_pages = {
            'dashboard': DashboardPage(),
            'inventory': InventoryPage(),
        }
        
        for page_id, page_widget in additional_pages.items():
            self.addWidget(page_widget)
            self.pages_map[page_id] = page_widget

    @staticmethod
    def _create_placeholder(name: str) -> QWidget:
        """
        Create a placeholder widget for pages not yet implemented.
        
        Args:
            name: The page name to display
            
        Returns:
            QWidget with placeholder content
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(f"{name}\n\n(Coming Soon)")
        layout.addWidget(label)
        layout.addStretch()
        return widget

    @Slot(str)
    def show_page(self, page_id: str) -> None:
        """
        Switch to page by identifier.
        
        Args:
            page_id: Page identifier string (e.g., 'dashboard', 'inventory')
        """
        if page_id in self.pages_map:
            widget = self.pages_map[page_id]
            self.setCurrentWidget(widget)

    def current_page(self) -> str:
        """
        Get the identifier of the currently displayed page.
        
        Returns:
            Page identifier string, or None if no page is active
        """
        current_widget = self.currentWidget()
        for page_id, widget in self.pages_map.items():
            if widget is current_widget:
                return page_id
        return None
