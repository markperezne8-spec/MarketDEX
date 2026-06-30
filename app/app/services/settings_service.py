from app.config.settings_manager import SettingsManager

class SettingsService:
    def __init__(self):
        self.manager=SettingsManager()

    def settings(self):
        return self.manager.load()

    def save(self,data):
        self.manager.save(data)
