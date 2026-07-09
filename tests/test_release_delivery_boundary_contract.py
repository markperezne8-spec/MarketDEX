from pathlib import Path


def test_release_delivery_boundary_excludes_installer_scope():
    boundary = Path('docs/RELEASE_DELIVERY_BOUNDARY.md').read_text(encoding='utf-8')

    assert 'operator-facing Windows RC delivery, not installer engineering' in boundary
    assert 'manually invokable Windows build' in boundary
    assert 'preserves source authority' in boundary
    assert 'Installer registration' in boundary
    assert 'code signing' in boundary
