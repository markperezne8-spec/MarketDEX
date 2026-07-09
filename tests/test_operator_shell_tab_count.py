from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_shell_has_three_primary_operator_workspaces():
    assert SOURCE.count('tabs.addTab(') == 2
    assert SOURCE.count('tabs.addTab(listing_page') == 1
    assert 'Listing Workflow' not in SOURCE.split('def install_viewport_fit_feature(window):', 1)[1].split("'Listings'", 1)[0]
