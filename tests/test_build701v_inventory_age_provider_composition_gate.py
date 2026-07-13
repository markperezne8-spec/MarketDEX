from pathlib import Path


DOC_PATH = Path('docs/reports/inventory_age_provider_composition_gate.md')


def test_build701v_composition_gate_preserves_application_owned_read_path() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'PREBUILD COMPOSITION GATE' in content
    assert 'composition/application_composition.py' in content
    assert 'Runtime-owned read-connection factory' in content
    assert 'InventoryDetailReadAdapter' in content
    assert 'InventoryProductLinkReadAdapter' in content
    assert 'ApplicationInventoryAgeInputProvider' in content
    assert 'Future composition-owned Reports query service' in content


def test_build701v_composition_gate_rejects_reports_persistence_and_early_wiring() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'This build adds no runtime wiring' in content
    assert 'Mark has pulled current `main` locally' in content
    assert 'opening SQLite connections' in content
    assert 'constructing `DatabaseManager`, `InventoryAppService`, or `InventoryProductLinkService`' in content
    assert '`found`, `not_found`, `unlinked`, `conflicting`, and `unavailable`' in content
    assert 'no database-manager construction or schema initialization occurs' in content
