import shutil
import sqlite3
from pathlib import Path

LEGACY_DATABASE_CANDIDATES = (
    Path('data/m51_m55_acceptance.sqlite3'),
)


def _inventory_count(path):
    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        return 0
    try:
        with sqlite3.connect(path) as connection:
            return int(connection.execute(
                "SELECT COUNT(*) FROM assets a JOIN inventory_authority i ON i.asset_id=a.asset_id WHERE a.state='COMPLETED'"
            ).fetchone()[0])
    except sqlite3.Error:
        return 0


def migrate_legacy_database_if_needed(runtime_path, project_root=None):
    runtime_path = Path(runtime_path)
    root = Path(project_root) if project_root is not None else runtime_path.parent.parent
    if _inventory_count(runtime_path) > 0:
        return None
    for relative_path in LEGACY_DATABASE_CANDIDATES:
        legacy_path = root / relative_path
        if _inventory_count(legacy_path) <= 0:
            continue
        runtime_path.parent.mkdir(parents=True, exist_ok=True)
        if runtime_path.exists():
            runtime_path.unlink()
        shutil.copy2(legacy_path, runtime_path)
        return legacy_path
    return None
