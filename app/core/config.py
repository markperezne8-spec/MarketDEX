from pathlib import Path

class Config:
    def __init__(self):
        self.app_name = "MarketDEX"
        self.version = "1.0.0 Alpha 1"
        self.database = Path("data/marketdex.db")
        self.theme = "dark"
