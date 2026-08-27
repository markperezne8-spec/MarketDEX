from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def _version_source() -> str:
    source = (ROOT / "version.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__ = "([^"]+)"$', source, re.MULTILINE)
    assert match, "version.py must define the canonical __version__ value"
    return match.group(1)


def test_release_version_is_consistent_across_runtime_and_windows_metadata():
    version = _version_source()
    major, minor, patch = version.split(".")

    desktop_version = (ROOT / "desktop" / "VERSION").read_text(encoding="utf-8").strip()
    installer = (ROOT / "installer" / "MarketDEX.iss").read_text(encoding="utf-8")
    launcher = (ROOT / "launcher.py").read_text(encoding="utf-8")

    assert desktop_version == version
    assert f'#define MyAppVersion "{version}"' in installer
    assert f"VersionInfoVersion={major}.{minor}.{patch}.0" in installer
    assert f"VersionInfoProductVersion={version}" in installer
    assert "from version import __version__" in launcher
    assert "APP_VERSION = __version__" in launcher
