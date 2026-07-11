from pathlib import Path


def test_start_here_preserves_permanent_project_memory_and_resume_order():
    text = Path('MARKETDEX_START_HERE.md').read_text(encoding='utf-8')

    for required in (
        'Enter once. Understand everywhere.',
        'Decisions first. Evidence second. Raw metrics on demand.',
        'MarketDEX_Mission_Control_Visual_North_Star.png',
        'MarketDEX_Official_Mascot.png',
        'FoundationCheckpoint.md',
        'Product_Vision_Idea_Register.md',
        'Canonical_Product_Terminology.md',
        'Modular_Collectibles_Platform_Blueprint.md',
        'Current_to_Target_Module_Map.md',
        'Architecture_Gates.md',
        'Canonical Domain, Identity, and Ownership Model',
        'Improve the existing MarketDEX foundation. Do not restart it',
    ):
        assert required in text


def test_start_here_keeps_desktop_first_and_future_platform_scope_clear():
    text = Path('MARKETDEX_START_HERE.md').read_text(encoding='utf-8')

    assert 'Windows desktop experience' in text
    assert 'iOS, Android, and browser clients remain future compatibility targets only' in text
    assert 'No mobile or web application tree during the desktop-first phase' in text
