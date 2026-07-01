REQUIRED={'version','application','window','workspace','autosave','theme','backup','recent_projects'}
def validate_configuration(cfg:dict)->bool:
    return REQUIRED.issubset(cfg.keys()) and cfg['window']['width']>0 and cfg['window']['height']>0
