import json
from pathlib import Path
from .defaults import DEFAULT_SETTINGS

class SettingsManager:
    def __init__(self,path="data/settings.json"):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)

    def load(self):
        if not self.path.exists():
            self.save(DEFAULT_SETTINGS)
        with open(self.path,"r",encoding="utf-8") as f:
            return json.load(f)

    def save(self,data):
        with open(self.path,"w",encoding="utf-8") as f:
            json.dump(data,f,indent=4)
