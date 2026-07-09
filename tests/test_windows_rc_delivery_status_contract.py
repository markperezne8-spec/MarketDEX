from pathlib import Path


def test_windows_rc_delivery_status_tracks_verified_and_next_boundaries():
    status = Path('docs/WINDOWS_RC_DELIVERY_STATUS.md').read_text(encoding='utf-8')

    assert 'Standalone Windows executable build verified' in status
    assert 'Operator download and clean launch verified' in status
    assert 'Generated executable remains separate from source authority' in status
    assert 'manual delivery workflow is the current hardening boundary' in status
    assert 'permanent release channel' in status
