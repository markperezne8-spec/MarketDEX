from app.engines.configuration.engine import ConfigurationEngine

def test_default_config_valid():
    engine=ConfigurationEngine()
    assert engine.validate()
