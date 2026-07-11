from pathlib import Path


def test_root_launcher_uses_the_existing_main_window_as_application_shell():
    project_root = Path(__file__).parents[1]
    launcher = (project_root / 'launcher.py').read_text(encoding='utf-8')
    main_window = (project_root / 'ui' / 'main_window.py').read_text(encoding='utf-8')

    assert 'from ui.main_window import MainWindow' in launcher
    assert 'window = MainWindow(mission_control, inventory)' in launcher
    assert 'def build_main_window(database_path: Path) -> MainWindow:' in launcher
    assert 'class MainWindow(QMainWindow):' in main_window
    assert 'window.showMaximized()' in launcher


def test_canonical_launcher_supplies_the_workspace_registry_to_the_existing_shell():
    project_root = Path(__file__).parents[1]
    launcher = (project_root / 'launcher.py').read_text(encoding='utf-8')

    assert 'from ui.workspace_registry import WorkspaceRegistry' in launcher
    assert 'workspace_registry = WorkspaceRegistry()' in launcher
    assert 'install_viewport_fit_feature(window, workspace_registry)' in launcher


def test_no_competing_desktop_launcher_or_shell_tree_exists():
    project_root = Path(__file__).parents[1]

    assert not (project_root / 'desktop' / 'launcher.py').exists()
    assert not (project_root / 'desktop' / 'ui' / 'app_shell.py').exists()
    assert not (project_root / 'ui' / 'app_shell.py').exists()
