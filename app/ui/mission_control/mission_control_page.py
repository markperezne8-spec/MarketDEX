"""
Mission Control Main Window
"""
from .layouts.dashboard_layout import DashboardLayout

class MissionControlPage:
    def __init__(self):
        self.layout=DashboardLayout()

    def load(self):
        return self.layout.build()
