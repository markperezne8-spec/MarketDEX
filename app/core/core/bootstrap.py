from app.core.lifecycle import ApplicationLifecycle
from app.core.application import MarketDEXApplication

def bootstrap():
    lifecycle = ApplicationLifecycle()
    lifecycle.startup()

    app = MarketDEXApplication()
    app.run()

    lifecycle.shutdown()
