from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_shell_moves_snapshot_cards_instead_of_cloning_them():
    extract = SOURCE[SOURCE.index('def _extract_mission_control'):SOURCE.index('def _install_listing_workflow_handoff')]
    assert 'takeAt(0)' in extract
    assert 'QGridLayout' not in extract
    assert 'window.values[' not in extract
