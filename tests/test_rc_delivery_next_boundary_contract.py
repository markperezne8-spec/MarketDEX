from pathlib import Path


def test_rc_delivery_next_boundary_is_release_channel_evaluation():
    boundary = Path('docs/RC_DELIVERY_NEXT_BOUNDARY.md').read_text(encoding='utf-8')

    assert 'permanent release-channel evaluation' in boundary
    assert 'GitHub Release asset' in boundary
    assert 'source/build/package separation' in boundary
    assert 'must not silently expand into installer or automatic-update engineering' in boundary
