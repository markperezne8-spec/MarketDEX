from pathlib import Path


def test_operator_shell_composition_does_not_import_business_authorities():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')

    assert 'repositories.' not in source
    assert 'services.' not in source
    assert 'sqlite3' not in source
    assert 'window.service.snapshot()' in source
