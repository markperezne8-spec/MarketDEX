from pathlib import Path


DOC_PATH = Path('docs/reports/inventory_age_application_read_dependency.md')


def test_inventory_age_read_dependency_document_exists() -> None:
    assert DOC_PATH.exists()


def test_reports_remains_a_read_only_consumer() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'Reports remains a consumer' in content
    assert 'must not query SQLite' in content
    assert 'must not query SQLite, `inventory_business_details`, `inventory_product_links`' in content
    assert 'No layer may create, repair, or mutate' in content


def test_provider_contract_preserves_deterministic_authority_boundaries() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'require an explicit as-of date' in content
    assert 'return `linked` only when exactly one canonical product ID is verified' in content
    assert 'preserve raw purchase-date text without parsing or rewriting it' in content
    assert 'avoid writes, events, audit entries' in content
    assert 'return deterministic results' in content


def test_build701m_selects_a_persistence_free_next_gate() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'Build 701N may add' in content
    assert 'must remain persistence-free' in content
    assert 'must not implement database reads' in content
    assert 'adds no provider implementation' in content
