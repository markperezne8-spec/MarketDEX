from pathlib import Path
import json
from .defaults import DEFAULT_CONFIGURATION
from .validation import validate_configuration

class ConfigurationEngine:
    def __init__(self, config_path: Path|None=None):
        self.config_path=config_path or Path("data/settings.json")
        self._config=DEFAULT_CONFIGURATION.copy()

    def load(self):
        if self.config_path.exists():
            self._config=json.loads(self.config_path.read_text())
        return self._config

    def save(self):
        self.config_path.parent.mkdir(parents=True,exist_ok=True)
        self.config_path.write_text(json.dumps(self._config,indent=2))
        return True

    def get(self,key,default=None):
        return self._config.get(key,default)

    def set(self,key,value):
        self._config[key]=value

    def validate(self):
        return validate_configuration(self._config)

    def reset(self):
        self._config=DEFAULT_CONFIGURATION.copy()

    def export_settings(self,path):
        Path(path).write_text(json.dumps(self._config,indent=2))

    def import_settings(self,path):
        self._config=json.loads(Path(path).read_text())
