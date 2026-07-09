from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_shell_recomposition_does_not_import_business_services_or_repositories():
    assert 'from services.' not in SOURCE
    assert 'from core.' not in SOURCE
    assert 'Repository' not in SOURCE
    assert '.database' not in SOURCE
