import logging
from pathlib import Path

def create_logger():
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        filename="logs/marketdex.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )
    logging.info("Logger initialized")
    return logging.getLogger("MarketDEX")
