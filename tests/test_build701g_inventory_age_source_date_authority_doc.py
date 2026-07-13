from pathlib import Path


DOC_PATH = Path('docs/reports/inventory_age_source_date_authority.md')


def test_source_date_authority_audit_exists() -> None:
    assert DOC_PATH.exists()


def test_purchase_date_is_the_only_approved_candidate() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'only currently approved candidate source date' in content
    assert 'InventoryAppService.get_asset_detail()' in content
    assert 'Reports must not substitute application record creation' in content
    assert 'whole calendar days from the current Inventory-owned purchase date' in content


def test_missing_and_invalid_dates_fail_closed() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'blank value as **unavailable**' in content
    assert 'valid ISO `YYYY-MM-DD` value as **available**' in content
    assert 'not a valid ISO calendar date as **invalid**' in content
    assert 'Unavailable is not zero' in content
    assert 'must not silently fall back' in content


def test_build701g_selects_persistence_free_adapter_gate() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'Build 701H may define' in content
    assert 'must not open a database' in content
    assert 'does not change existing Inventory write validation' in content
    assert 'adds no runtime code' in content
