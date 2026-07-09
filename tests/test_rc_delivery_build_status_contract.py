from pathlib import Path


def test_rc_delivery_build_status_keeps_operator_action_explicit():
    status = Path('docs/RC_DELIVERY_BUILD_STATUS.md').read_text(encoding='utf-8')

    assert 'implementation complete; pull-request CI verification required' in status
    assert 'Operator action: none until the pull request merges' in status
    assert '`🟢 PULL NOW`' in status
