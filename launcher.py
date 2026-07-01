"""
MarketDEX Launcher
"""

from app.core.bootstrap import bootstrap
from app.core.application import run

if __name__ == "__main__":
    lifecycle = bootstrap()
    try:
        run()
    finally:
        lifecycle.shutdown()
