"""GUI app implementation."""
import qdarktheme  # type: ignore

from win_caffeine import qt
from win_caffeine import settings
from win_caffeine import theme
from win_caffeine import main_window


def run(args) -> int:
    """Run GUI app."""

    del args  # unused
    # Enable HiDPI.
    qdarktheme.enable_hi_dpi()

    # Create the application
    app = qt.QApplication([])
    theme.set_theme("auto", app)

    # Create the main window
    window = main_window.MainWindow()

    # Create the system tray icon
    tray_icon = qt.QSystemTrayIcon(qt.QIcon(theme.icon_path.coffee_on), parent=app)
    tray_icon.setToolTip(window.windowTitle())

    # Create the system tray menu
    tray_menu = qt.QMenu()
    tray_menu.addAction("Restore", window.showNormal)  # Restore the main window
    tray_menu.addAction("Exit", window.on_quit)  # Quit the application
    tray_icon.setContextMenu(tray_menu)

    # Show the main window
    window.show()
    # Tray icon to minimize to system tray
    tray_icon.show()

    if settings.START_IN_SUSPEND_MODE:
        window.toggle_button.click()

    app.setQuitOnLastWindowClosed(False)

    # Start the application event loop
    return app.exec_()
