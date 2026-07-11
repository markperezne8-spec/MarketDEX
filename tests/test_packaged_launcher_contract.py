import os
import sys
from pathlib import Path

import launcher


def test_source_runtime_stays_inside_repository(monkeypatch, tmp_path):
    monkeypatch.delenv('MARKETDEX_DATA_DIR', raising=False)
    monkeypatch.setattr(sys, 'frozen', False, raising=False)
    monkeypatch.setattr(launcher, 'source_root', lambda: tmp_path)
    assert launcher.application_data_dir() == tmp_path / 'runtime'
    assert launcher.runtime_database_path() == tmp_path / 'runtime' / 'marketdex.sqlite3'


def test_packaged_runtime_uses_local_app_data(monkeypatch, tmp_path):
    monkeypatch.delenv('MARKETDEX_DATA_DIR', raising=False)
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    assert launcher.application_data_dir() == tmp_path / 'MarketDEX'
    assert launcher.runtime_database_path() == tmp_path / 'MarketDEX' / 'marketdex.sqlite3'


def test_data_directory_override_is_authoritative(monkeypatch, tmp_path):
    override = tmp_path / 'portable-data'
    monkeypatch.setenv('MARKETDEX_DATA_DIR', str(override))
    assert launcher.application_data_dir() == override.resolve()


def test_verify_runtime_initializes_database_without_opening_window(monkeypatch, tmp_path):
    monkeypatch.setenv('MARKETDEX_DATA_DIR', str(tmp_path))
    result = launcher.main(['MarketDEX.exe', '--verify-runtime'])
    assert result == 0
    assert (tmp_path / 'marketdex.sqlite3').exists()
