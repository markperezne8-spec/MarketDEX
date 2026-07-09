from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_primary_tab_labels_are_concise_and_unique():
    labels = ['Mission Control', 'Inventory & Pricing', 'Listings']
    for label in labels:
        assert f"'{label}'" in SOURCE
    assert len(set(labels)) == 3
