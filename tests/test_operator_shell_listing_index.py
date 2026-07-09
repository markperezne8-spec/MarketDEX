from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_listing_handoff_does_not_depend_on_hard_coded_tab_number():
    handoff = SOURCE[SOURCE.index('def _install_listing_workflow_handoff'):SOURCE.index('def install_viewport_fit_feature')]
    assert 'setCurrentIndex(listing_index)' in handoff
    assert 'setCurrentIndex(1)' not in handoff
    assert 'setCurrentIndex(2)' not in handoff
