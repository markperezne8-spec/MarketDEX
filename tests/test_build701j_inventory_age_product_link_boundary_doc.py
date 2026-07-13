from pathlib import Path


DOC_PATH = Path('docs/reports/inventory_age_product_link_integration_boundary.md')


def test_product_link_integration_boundary_exists() -> None:
    assert DOC_PATH.exists()


def test_reports_cannot_synthesize_product_identity() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'lacks canonical Product Registry identity' in content
    assert 'must not create substitute product identity' in content
    assert 'asset identifier, asset name, or asset type' in content
    assert 'Existing Inventory detail output does not contain a canonical `product_id`' in content


def test_product_link_evidence_fails_closed() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert '**linked**' in content
    assert '**unlinked**' in content
    assert '**conflicting**' in content
    assert 'must fail closed before an Inventory Age row is created' in content


def test_build701j_selects_a_narrow_persistence_free_gate() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'Build 701K may introduce' in content
    assert 'must not access a database' in content
    assert 'or wire application composition' in content
    assert 'adds no runtime integration' in content
