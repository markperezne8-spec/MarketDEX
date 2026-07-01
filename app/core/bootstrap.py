"""
Bootstrap for MarketDEX.
Keeps startup orchestration in one place.
"""

from app.core.version import APP_NAME, VERSION
from app.core.lifecycle import ApplicationLifecycle

def bootstrap():
    lifecycle = ApplicationLifecycle()
    lifecycle.startup()

    print(f"{APP_NAME} {VERSION}")
    # Future:
    # - load configuration
    # - initialize logging
    # - initialize database
    # - register services

    return lifecycle
