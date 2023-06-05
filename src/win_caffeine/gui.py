"""GUI app implementation."""
from win_caffeine import settings
from win_caffeine import qt
from win_caffeine import screen_lock
from win_caffeine import main_window


def run(*args, **kwargs):
    """Run GUI app."""

    # Clear existing state
    screen_lock.release_screen_lock()

    settings.init()
    # Create the application
    app = qt.QApplication([])
    settings.set_theme("auto")

    icon_path = settings.IconPath.coffee_off
    if screen_lock.is_on():
        icon_path = settings.IconPath.coffee_on

    # Create the main window
    window = main_window.MainWindow()
    window.setWindowTitle(settings.APP_NAME)
    window.setWindowIcon(qt.QIcon(icon_path))
    window.setFixedWidth(settings.WINDOW_FIXED_WIDTH)
    window.setFixedHeight(settings.WINDOW_FIXED_HEIGHT)

    # Create the system tray icon
    tray_icon = qt.QSystemTrayIcon(qt.QIcon(icon_path), parent=app)
    tray_icon.setToolTip(settings.APP_NAME)

    # Create the system tray menu
    tray_menu = qt.QMenu()
    tray_menu.addAction("Restore", window.showNormal)  # Restore the main window
    tray_menu.addAction("Exit", app.quit)  # Quit the application
    tray_icon.setContextMenu(tray_menu)

    # Show the main window
    window.show()

    # Minimize to system tray
    tray_icon.show()
    app.setQuitOnLastWindowClosed(False)

    # Start the application event loop
    return app.exec_()
