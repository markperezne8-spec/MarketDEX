from services.product_registry_lookup_service import ProductRegistryLookupService
from services.product_registry_service import ProductRegistryService


def _counts(service):
    with service.database.read_connection() as connection:
        return {
            'products': connection.execute('SELECT COUNT(*) n FROM products').fetchone()['n'],
            'aliases': connection.execute('SELECT COUNT(*) n FROM product_aliases').fetchone()['n'],
            'events': connection.execute('SELECT COUNT(*) n FROM event_identity').fetchone()['n'],
            'audit': connection.execute('SELECT COUNT(*) n FROM audit_events').fetchone()['n'],
        }


def test_cap005c_lookup_finds_canonical_alias_and_product_id_without_mutation(tmp_path):
    database_path = tmp_path / 'marketdex.db'
    registry = ProductRegistryService(database_path)
    product_id = registry.register(
        'SINGLE', 'Charizard ex', 'Obsidian Flames', '125/197', 'Double Rare',
        'CAP005C-REGISTER-001',
    )
    registry.add_alias(product_id, 'Charizard EX 125/197', 'CAP005C-ALIAS-001')
    before = _counts(registry)

    lookup = ProductRegistryLookupService(database_path)
    assert lookup.by_product_id(product_id).canonical_name == 'Charizard ex'
    assert lookup.search('Charizard ex')[0].product_id == product_id
    assert lookup.search('Charizard EX 125/197')[0].matched_by == 'ALIAS'
    assert lookup.search('125/197')[0].card_number == '125/197'
    assert lookup.search('Obsidian Flames', product_type='SINGLE')[0].product_id == product_id
    assert _counts(registry) == before


def test_cap005c_lookup_is_deterministic_restart_safe_and_fail_safe(tmp_path):
    database_path = tmp_path / 'marketdex.db'
    registry = ProductRegistryService(database_path)
    single_id = registry.register(
        'SINGLE', 'Pikachu ex', 'Surging Sparks', '057/191', 'Double Rare',
        'CAP005C-REGISTER-002',
    )
    sealed_id = registry.register(
        'SEALED', 'Surging Sparks Elite Trainer Box', 'Surging Sparks', None, 'Standard',
        'CAP005C-REGISTER-003',
    )

    first = ProductRegistryLookupService(database_path)
    restarted = ProductRegistryLookupService(database_path)

    assert first.search('Surging Sparks') == restarted.search('Surging Sparks')
    assert {row.product_id for row in first.search('Surging Sparks')} == {single_id, sealed_id}
    assert tuple(row.product_id for row in first.search('Surging Sparks', product_type='SEALED')) == (sealed_id,)
    assert first.search('') == ()
    assert first.search('does not exist') == ()
    assert first.by_product_id('') is None
