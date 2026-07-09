from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AppConfig:
    app_name: str
    app_version: str
    specification_build: str
    project_root: Path
    data_dir: Path
    database_path: Path
    log_dir: Path


def load_config() -> AppConfig:
    desktop_root = Path(__file__).resolve().parents[1]
    project_root = desktop_root.parent
    version_path = desktop_root / "VERSION"
    app_version = version_path.read_text(encoding="utf-8").strip()
    data_dir = desktop_root / "data"
    log_dir = desktop_root / "logs"
    data_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    return AppConfig(
        app_name="MarketDEX OS",
        app_version=app_version,
        specification_build="503",
        project_root=project_root,
        data_dir=data_dir,
        database_path=data_dir / "marketdex.db",
        log_dir=log_dir,
    )
