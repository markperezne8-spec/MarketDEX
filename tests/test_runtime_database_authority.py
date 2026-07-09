from pathlib import Path

import launcher


def test_runtime_database_is_separate_from_repository_acceptance_data():
    path = launcher.runtime_database_path()
    assert path.name == 'marketdex.sqlite3'
    assert path.parent.name == 'runtime'
    assert 'm51_m55_acceptance' not in str(path)


def test_runtime_database_patterns_are_git_ignored():
    gitignore = Path('.gitignore').read_text(encoding='utf-8')
    assert 'runtime/' in gitignore
    assert '*.sqlite3' in gitignore
    assert '*.sqlite3-shm' in gitignore
    assert '*.sqlite3-wal' in gitignore
