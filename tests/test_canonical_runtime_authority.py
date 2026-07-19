from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


CANONICAL_RUNTIME_FILES = (
    'launcher.py',
    'composition/application_composition.py',
    'composition/feature_catalog.py',
    'ui/main_window.py',
)


def test_launcher_and_packaging_use_canonical_root_entrypoint():
    launcher = (ROOT / 'launcher.py').read_text(encoding='utf-8')
    spec = (ROOT / 'MarketDEX.spec').read_text(encoding='utf-8')

    assert 'from composition import ApplicationComposition' in launcher
    assert 'from ui.main_window import MainWindow' in launcher
    assert "['launcher.py']" in spec
    assert 'app/ui' not in spec
    assert 'app/database' not in spec


def test_canonical_runtime_does_not_import_legacy_app_authorities():
    forbidden_prefixes = (
        'from app.ui',
        'import app.ui',
        'from app.services',
        'import app.services',
        'from app.database',
        'import app.database',
        'from app.repositories',
        'import app.repositories',
    )

    violations = []
    for relative_path in CANONICAL_RUNTIME_FILES:
        content = (ROOT / relative_path).read_text(encoding='utf-8')
        for line_number, line in enumerate(content.splitlines(), start=1):
            if line.strip().startswith(forbidden_prefixes):
                violations.append(f'{relative_path}:{line_number}: {line.strip()}')

    assert not violations, '\\n'.join(violations)


def test_legacy_tree_remains_explicitly_noncanonical():
    assert (ROOT / 'app/ui').is_dir()
    assert (ROOT / 'app/services').is_dir()
    assert (ROOT / 'app/database').is_dir()
    assert (ROOT / 'ui').is_dir()
    assert (ROOT / 'services').is_dir()
    assert (ROOT / 'composition').is_dir()
