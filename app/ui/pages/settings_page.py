from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SettingsPage(QWidget):
    """Settings page for application configuration."""
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Settings\n\n(Coming Soon)")
        layout.addWidget(label)
        layout.addStretch()
