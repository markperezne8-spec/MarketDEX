from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    desktop_root = Path(__file__).resolve().parent
    if str(desktop_root) not in sys.path:
        sys.path.insert(0, str(desktop_root))

    from app.main import run

    return run()


if __name__ == "__main__":
    raise SystemExit(main())
