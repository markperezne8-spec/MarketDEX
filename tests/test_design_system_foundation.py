from pathlib import Path

from ui.design_system.component_contracts import ComponentState, build_component_catalog
from ui.design_system.tokens import (
    ColorRole,
    Density,
    NorthStarPanelTone,
    SpacingRole,
    TypographyRole,
    build_visual_north_star_tokens,
)


def test_visual_north_star_document_preserves_approved_identity_and_direction():
    text = Path('docs/design/VISUAL_NORTH_STAR.md').read_text(encoding='utf-8')

    for required in (
        'Design Locked · Permanent Product Direction',
        'assets/brand/visual_north_star/marketdex_visual_north_star_v1.png',
        '1269e2af119c569cc5d4f76b82a6f92984a04f6f752119d8e1dcf417557909a5',
        'MarketDEX_Official_Mascot.png',
        'Business Mode and Collector Mode',
        'Gamification and engagement',
        'trainer level',
        'daily quests or objectives',
        'Mission Control is the flagship implementation',
        'Do not:',
        'attempt one massive UI rewrite',
        'claim completion when only a static mockup exists',
    ):
        assert required in text


def test_visual_north_star_tokens_are_complete_semantic_and_valid():
    tokens = build_visual_north_star_tokens()

    assert tokens.version == 'visual-north-star-v1.0'
    assert tokens.visual_authority.endswith('marketdex_visual_north_star_v1.png')
    assert set(tokens.colors) == set(ColorRole)
    assert set(tokens.typography) == set(TypographyRole)
    assert set(tokens.spacing) == set(SpacingRole)
    assert set(tokens.densities) == set(Density)
    assert set(tokens.north_star_panel_tones) == set(NorthStarPanelTone)
    assert tokens.color(ColorRole.APP_BACKGROUND).startswith('#')
    assert tokens.color(ColorRole.FOCUS_RING) != tokens.color(ColorRole.APP_BACKGROUND)
    assert tokens.densities[Density.LARGE_TEXT].control_height > (
        tokens.densities[Density.STANDARD].control_height
    )
    tokens.validate()


def test_visual_north_star_panel_tones_map_to_existing_color_roles():
    tokens = build_visual_north_star_tokens()

    assert tokens.north_star_panel_tones[NorthStarPanelTone.OPPORTUNITY] == (
        ColorRole.OPPORTUNITY
    )
    assert tokens.north_star_panel_tones[NorthStarPanelTone.RISK] == (
        ColorRole.NEGATIVE
    )
    assert tokens.north_star_panel_tones[NorthStarPanelTone.SCOREBOARD] == (
        ColorRole.PRIMARY_ACTION
    )


def test_component_catalog_has_unique_ids_and_required_foundation_components():
    components = build_component_catalog()
    component_ids = {component.component_id for component in components}

    assert len(component_ids) == len(components)
    assert {
        'application-shell',
        'navigation-item',
        'workspace-header',
        'kpi-card',
        'dashboard-panel',
        'status-badge',
        'attention-row',
        'opportunity-card',
        'recommendation-card',
        'chart-container',
        'data-table',
        'filter-bar',
        'search-control',
        'mode-selector',
        'empty-state',
        'loading-state',
        'error-state',
        'confirmation-dialog',
        'detail-drawer',
        'mascot-guidance-panel',
        'assistant-launcher',
        'progress-card',
    }.issubset(component_ids)

    for component in components:
        component.validate()
        assert ComponentState.DEFAULT in component.required_states
        assert component.keyboard_requirement.strip()
        assert component.accessibility_requirement.strip()


def test_design_system_foundation_remains_pyside_independent():
    for path in (
        Path('ui/design_system/tokens.py'),
        Path('ui/design_system/component_contracts.py'),
    ):
        text = path.read_text(encoding='utf-8')
        assert 'PySide6' not in text
        assert 'sqlite3' not in text


def test_brand_asset_directories_record_expected_visual_and_mascot_identities():
    visual = Path('assets/brand/visual_north_star/README.md').read_text(
        encoding='utf-8'
    )
    mascot = Path('assets/brand/mascot/README.md').read_text(encoding='utf-8')

    assert 'marketdex_visual_north_star_v1.png' in visual
    assert '27d4b34b24984678225ae38c7e77240a02d521b4' in visual
    assert 'marketdex_official_mascot.png' in mascot
    assert '5c192e8833896cf754f20fcb636d30098bc75ecf' in mascot
