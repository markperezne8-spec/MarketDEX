from pathlib import Path


def test_architecture_gate_framework_is_repository_authority():
    text = Path('docs/governance/Architecture_Gates.md').read_text(encoding='utf-8')

    for gate in (
        'Vision continuity gate',
        'Authority gate',
        'Architecture gate',
        'Terminology compatibility gate',
        'Visual identity gate',
        'Behavior gate',
        'Data gate',
        'UX gate',
        'Integration gate',
        'Platform compatibility gate',
        'AI safety gate',
        'Packaging gate',
        'Release gate',
    ):
        assert gate in text

    assert 'Every material pull request must record' in text
    assert 'No material approved idea may exist only in chat memory' in text
    assert 'No new user-facing top-level name' in text
    assert 'No major UI delivery that ignores the Visual North Star' in text
    assert 'No replacement, deletion, redesign, recoloring' in text
    assert 'No second launcher, shell, database authority' in text
    assert 'No active mobile or web application tree' in text
    assert 'No direct AI mutation of SQLite' in text


def test_platform_strategy_is_desktop_first_and_future_compatible():
    text = Path('docs/governance/Platform_Strategy.md').read_text(encoding='utf-8')

    assert 'Windows desktop application first' in text
    assert 'No iOS, Android, or browser application is currently in scope' in text
    assert 'must not depend on PySide6 widgets' in text
    assert 'Funko Pops' in text
    assert 'controlled commands and read models' in text


def test_approved_architecture_roadmap_records_product_owner_authority():
    text = Path('docs/governance/Approved_Architecture_Roadmap.md').read_text(
        encoding='utf-8'
    )

    assert 'Product Owner approved' in text
    assert 'Pokémon TCG' in text
    assert 'future iOS, Android, and web compatibility' in text
    assert 'Canonical shell and workspace authority' in text
    assert 'Architecture enforcement in CI' in text
    assert 'does not authorize destructive data changes' in text
    assert 'Product_Vision_Idea_Register.md' in text
    assert 'Canonical_Product_Terminology.md' in text


def test_product_vision_register_preserves_approved_scope_and_ideas():
    text = Path('docs/governance/Product_Vision_Idea_Register.md').read_text(
        encoding='utf-8'
    )

    for required in (
        'Decisions first. Evidence second. Raw metrics on demand.',
        'Pokémon TCG',
        'Funko Pops',
        'Business Mode',
        'Collector Mode',
        'Market Compass',
        'Collector Pulse',
        'Google Trends',
        'daily sold-volume',
        'heat maps',
        'KEEP SEALED',
        'controlled application contracts',
        'APPROVED — FUTURE',
    ):
        assert required in text

    assert 'No chat summary alone is product authority' in text


def test_canonical_product_terminology_resolves_known_conflicts():
    text = Path('docs/governance/Canonical_Product_Terminology.md').read_text(
        encoding='utf-8'
    )

    for required in (
        'Dashboard → Mission Control',
        'Platform → Marketplace',
        'Asset Manager → Inventory or Collection',
        'Business module → Business Operations',
        'Alerts / Attention Center → Needs Attention',
        'Listing Workflow → Listings',
        'Personal Collection → Collection',
        'Marketplace Dashboard / Platform Analysis → Market Compass',
        'Market Pulse → Collector Pulse',
    ):
        assert required in text

    assert 'controlled compatibility migration' in text


def test_visual_north_star_and_mascot_standard_is_permanent_authority():
    text = Path(
        'docs/governance/Visual_North_Star_and_Mascot_Standard.md'
    ).read_text(encoding='utf-8')

    for required in (
        'Permanent Product Requirement',
        'MarketDEX_Mission_Control_Visual_North_Star.png',
        'MarketDEX_Official_Mascot.png',
        'permanent MarketDEX brand element',
        'No release may silently omit the mascot',
        'shared design system',
        'packaged executable and installer builds',
    ):
        assert required in text


def test_modular_platform_blueprint_preserves_desktop_and_future_boundaries():
    text = Path(
        'docs/Architecture/Modular_Collectibles_Platform_Blueprint.md'
    ).read_text(encoding='utf-8')

    for required in (
        'Windows Desktop Presentation',
        'Application Layer',
        'Domain Layer',
        'Infrastructure Adapters',
        'one application composition root',
        'Catalog',
        'Inventory',
        'Collection',
        'Market Data',
        'AI is an authorized application client',
        'No cloud sync is required now',
        'Only canonical persistence infrastructure may open SQLite connections',
    ):
        assert required in text


def test_current_to_target_module_map_protects_migration_classification():
    text = Path('docs/Architecture/Current_to_Target_Module_Map.md').read_text(
        encoding='utf-8'
    )

    for classification in ('KEEP', 'ADAPT', 'MIGRATE', 'RETIRE', 'REVIEW'):
        assert classification in text

    for required in (
        'root `launcher.py`',
        'root `ui/main_window.py`',
        '`core/schema.py`',
        '`core/database_manager.py`',
        '`app/database/database_manager.py`',
        '`services/inventory_app_service.py`',
        '`services/mission_control_service.py`',
        '`services/dashboard_service.py`',
        '`market_intelligence/*` contracts',
        'never deleted by assumption',
    ):
        assert required in text


def test_ec005_records_current_stacked_history_and_exact_resume_point():
    text = Path(
        'docs/checkpoints/EC-005_Shell_Composition_Market_Intelligence.md'
    ).read_text(encoding='utf-8')

    for pull_request in ('PR #163', 'PR #164', 'PR #165', 'PR #166'):
        assert pull_request in text

    assert 'Mandatory checkpoint results' in text
    assert 'Platform compatibility' in text
    assert 'AI safety' in text
    assert 'Exact resume point' in text
    assert 'Collection Overview Workspace' in text


def test_ec006_records_vision_continuity_naming_and_deferred_fix():
    text = Path(
        'docs/checkpoints/EC-006_Vision_Continuity_Modular_Platform_Naming.md'
    ).read_text(encoding='utf-8')

    assert 'Product Owner approved all available prior MarketDEX' in text
    assert 'Product_Vision_Idea_Register.md' in text
    assert 'Canonical_Product_Terminology.md' in text
    assert 'Modular_Collectibles_Platform_Blueprint.md' in text
    assert 'Current_to_Target_Module_Map.md' in text
    assert 'Listing gate remains failing' in text
    assert 'Exact resume point' in text


def test_ec007_records_visual_identity_and_mascot_lock():
    text = Path(
        'docs/checkpoints/EC-007_Visual_North_Star_Mascot_Lock.md'
    ).read_text(encoding='utf-8')

    assert 'Visual North Star' in text
    assert 'MarketDEX_Official_Mascot.png' in text
    assert 'exact approved asset identities' in text
    assert 'Visual identity gate' in text
    assert 'Exact resume point' in text
