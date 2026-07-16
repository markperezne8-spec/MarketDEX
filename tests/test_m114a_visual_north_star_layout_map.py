from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
NORTH_STAR_IMAGE = REPOSITORY_ROOT / 'MarketDEX_Mission_Control_Visual_North_Star.png'
LAYOUT_MAP = (
    REPOSITORY_ROOT
    / 'docs'
    / 'checkpoints'
    / 'M1.14A-visual-north-star-layout-map.md'
)


def test_visual_north_star_source_image_exists():
    assert NORTH_STAR_IMAGE.is_file()


def test_visual_north_star_layout_map_names_required_regions():
    source = LAYOUT_MAP.read_text(encoding='utf-8')

    required_regions = (
        'Brand + mascot header',
        'Period/date/status band',
        'Left navigation rail',
        "Today's Top 3",
        'Capital Health',
        'Opportunity + Risk',
        'Business Scoreboard',
        'Inventory Command Center',
        'Inventory Breakdown table',
        'Inventory Alerts',
        'Visual Intelligence',
        'Footer operating strip',
    )

    for region in required_regions:
        assert region in source


def test_visual_north_star_layout_map_preserves_boundaries():
    source = LAYOUT_MAP.read_text(encoding='utf-8')

    assert 'Visual-only now' in source
    assert 'Contract-first' in source
    assert 'no fake live data' in source
    assert 'no UI implementation' in source
    assert 'no live checks' in source


def test_m114a_does_not_authorize_runtime_or_mutation_scope():
    source = LAYOUT_MAP.read_text(encoding='utf-8')

    prohibited_scope = (
        'marketplace integration',
        'network access',
        'polling',
        'alerts',
        'notifications',
        'persistence',
        'database migration',
        'dependency changes',
        'business mutation',
    )

    for phrase in prohibited_scope:
        assert phrase in source
