from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
DATABASE_DIR = DATA_DIR / "database"
LOG_DIR = DATA_DIR / "logs"
EXPORT_DIR = PROJECT_ROOT / "exports"
BACKUP_DIR = PROJECT_ROOT / "backups"
ASSETS_DIR = PROJECT_ROOT / "assets"

for d in (DATA_DIR, DATABASE_DIR, LOG_DIR, EXPORT_DIR, BACKUP_DIR):
    d.mkdir(parents=True, exist_ok=True)
