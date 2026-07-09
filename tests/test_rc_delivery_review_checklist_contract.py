from pathlib import Path


def test_rc_delivery_review_checklist_preserves_release_hardening_rules():
    checklist = Path('docs/RC_DELIVERY_REVIEW_CHECKLIST.md').read_text(encoding='utf-8')

    assert 'delivery workflow is manual' in checklist
    assert 'authoritative `launcher.py` packaging specification' in checklist
    assert 'verification occurs before artifact publication' in checklist
    assert 'extract outside the repository' in checklist
    assert 'no generated `.exe` is committed' in checklist
    assert 'installer and automatic-update scope remain excluded' in checklist
