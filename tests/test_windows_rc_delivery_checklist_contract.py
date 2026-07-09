from pathlib import Path


def test_windows_rc_delivery_checklist_preserves_operator_sequence():
    checklist = Path('docs/WINDOWS_RC_DELIVERY_CHECKLIST.md').read_text(encoding='utf-8')

    expected = [
        'Source authority stays in Git',
        'Run `Windows RC Delivery` manually',
        'verifies `MarketDEX.exe` before staging delivery',
        'Download `MarketDEX-Windows-RC-Operator-Package`',
        'Extract the package outside the source repository',
        'Launch `MarketDEX.exe`',
        'Confirm the first MarketDEX window opens successfully',
        'Never commit the generated executable',
    ]
    positions = [checklist.index(item) for item in expected]
    assert positions == sorted(positions)
