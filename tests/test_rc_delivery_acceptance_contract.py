from pathlib import Path


def test_rc_delivery_acceptance_requires_full_operator_path():
    acceptance = Path('docs/RC_DELIVERY_ACCEPTANCE.md').read_text(encoding='utf-8')

    for requirement in (
        'manual Windows RC Delivery workflow',
        'non-empty `MarketDEX.exe`',
        '`README.txt` guidance',
        '`MarketDEX-Windows-RC-Operator-Package`',
        'download, extract outside the repository, and clean-launch MarketDEX',
    ):
        assert requirement in acceptance
