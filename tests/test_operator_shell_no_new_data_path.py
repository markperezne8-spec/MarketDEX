from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_shell_has_no_file_database_or_network_io():
    for forbidden in ('sqlite3', 'requests', 'urllib', 'open(', 'Path('):
        assert forbidden not in SOURCE
