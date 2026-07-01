def build_menu(window):
    m=window.menuBar()
    for name in ("File","View","Tools","Help"):
        m.addMenu(name)
