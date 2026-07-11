from pathlib import Path


def test_installer_packages_the_verified_root_executable_per_user():
    project_root = Path(__file__).parents[1]
    installer = (project_root / 'installer' / 'MarketDEX.iss').read_text(encoding='utf-8')

    assert 'Source: "..\\dist\\MarketDEX.exe"' in installer
    assert 'OutputBaseFilename=MarketDEX_Setup' in installer
    assert 'DefaultDirName={localappdata}\\Programs\\MarketDEX' in installer
    assert 'PrivilegesRequired=lowest' in installer
    assert 'Name: "{group}\\MarketDEX OS"' in installer
    assert 'Name: "{autodesktop}\\MarketDEX OS"' in installer


def test_installer_does_not_bundle_or_delete_user_database_authority():
    project_root = Path(__file__).parents[1]
    installer = (project_root / 'installer' / 'MarketDEX.iss').read_text(encoding='utf-8')

    assert 'marketdex.sqlite3' not in installer
    assert '[UninstallDelete]' not in installer
    assert 'runtime\\' not in installer


def test_windows_ci_builds_and_verifies_the_installer():
    project_root = Path(__file__).parents[1]
    workflow = (project_root / '.github' / 'workflows' / 'ci.yml').read_text(encoding='utf-8')

    assert 'choco install innosetup' in workflow
    assert 'installer\\MarketDEX.iss' in workflow
    assert 'MarketDEX_Setup.exe' in workflow
    assert 'MarketDEX-Installer' in workflow
    assert '--verify-runtime' in workflow
