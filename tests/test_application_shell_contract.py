from pathlib import Path


def test_root_launcher_delegates_to_the_canonical_application_composition():
    project_root = Path(__file__).parents[1]
    launcher = (project_root / 'launcher.py').read_text(encoding='utf-8')
    composition = (
        project_root / 'composition' / 'application_composition.py'
    ).read_text(encoding='utf-8')
    main_window = (project_root / 'ui' / 'main_window.py').read_text(encoding='utf-8')

    assert 'from composition import ApplicationComposition' in launcher
    assert 'return ApplicationComposition(database_path)' in launcher
    assert 'return build_application(database_path).build_main_window()' in launcher
    assert 'window = composition.build_main_window()' in launcher
    assert 'window.showMaximized()' in launcher
    assert 'availableGeometry()' in launcher
    assert 'window = MainWindow(self.mission_control, self.inventory)' in composition
    assert 'class MainWindow(QMainWindow):' in main_window


def test_composition_owns_the_single_workspace_registry_and_feature_catalog_path():
    project_root = Path(__file__).parents[1]
    launcher = (project_root / 'launcher.py').read_text(encoding='utf-8')
    composition = (
        project_root / 'composition' / 'application_composition.py'
    ).read_text(encoding='utf-8')

    assert 'WorkspaceRegistry' not in launcher
    assert 'install_inventory_' not in launcher
    assert 'self.workspace_registry = WorkspaceRegistry()' in composition
    assert 'install_features(window)' in composition
    assert 'install_viewport_fit_feature(window, self.workspace_registry)' in composition


def test_no_competing_desktop_launcher_or_shell_tree_exists():
    project_root = Path(__file__).parents[1]

    assert not (project_root / 'desktop' / 'launcher.py').exists()
    assert not (project_root / 'desktop' / 'ui' / 'app_shell.py').exists()
    assert not (project_root / 'ui' / 'app_shell.py').exists()
