from app.engines.configuration import ConfigurationEngine
def test_defaults():
    e=ConfigurationEngine()
    assert e.get("version")==1
