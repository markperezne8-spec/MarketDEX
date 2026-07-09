from pathlib import Path


def test_rc_delivery_handoff_keeps_pull_build_and_package_separate():
    handoff = Path('docs/RC_DELIVERY_HANDOFF.md').read_text(encoding='utf-8')

    assert '⬇️ source pull -> 📦 delivery build -> 🪟 operator package' in handoff
    assert 'source pull updates the permanent codebase' in handoff
    assert 'delivery build generates and verifies the Windows executable' in handoff
    assert 'operator package is downloaded and run outside the source repository' in handoff
    assert 'must not be presented as interchangeable' in handoff
