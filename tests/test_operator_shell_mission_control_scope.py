from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_mission_control_contains_snapshot_and_guidance_not_listing_stages():
    extract = SOURCE[SOURCE.index('def _extract_mission_control'):SOURCE.index('def _install_listing_workflow_handoff')]
    assert 'cards_item' in extract
    assert 'Your business at a glance.' in extract
    assert 'LISTING_WORKFLOW_WIDGETS' not in extract
