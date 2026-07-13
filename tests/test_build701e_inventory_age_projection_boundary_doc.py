from pathlib import Path


DOC_PATH = Path('docs/reports/inventory_age_projection_boundary.md')


def test_inventory_age_projection_boundary_exists() -> None:
    assert DOC_PATH.exists()


def test_projection_preserves_inventory_source_authority() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'Inventory remains the sole source domain' in content
    assert 'open SQLite directly' in content
    assert 'Reports owns only an immutable presentation read model' in content
    assert 'No monetary value, market price, profit' in content


def test_projection_requires_explicit_deterministic_time_meaning() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'use an explicit as-of date' in content
    assert 'whole elapsed calendar days deterministically' in content
    assert 'Unavailable is not zero' in content
    assert 'avoid wall-clock-dependent test behavior' in content


def test_build701e_selects_narrow_non_runtime_gate() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'Build 701E defines the boundary only' in content
    assert 'Build 701F may introduce' in content
    assert 'persistence-free, composition-free, UI-free, export-free' in content
    assert 'exact Inventory start-date authority' in content
