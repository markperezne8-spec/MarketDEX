from app.core.config import Config
from app.core.logger import create_logger
from app.core.service_registry import ServiceRegistry

def startup():
    config = Config()
    logger = create_logger()
    registry = ServiceRegistry()

    registry.register("config", config)
    registry.register("logger", logger)

    logger.info("Startup completed")
    return registry
