from typing import TypedDict, NotRequired

class WindowConfig(TypedDict):
    width:int
    height:int
    maximized:bool

class AutoSaveConfig(TypedDict):
    enabled:bool
    interval:int

class ThemeConfig(TypedDict):
    mode:str

class ConfigurationSchema(TypedDict):
    version:int
    application:dict
    window:WindowConfig
    workspace:dict
    autosave:AutoSaveConfig
    theme:ThemeConfig
    backup:dict
    recent_projects:list[str]
    experimental:NotRequired[dict]
