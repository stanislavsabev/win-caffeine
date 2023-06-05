"""GUI app implementation."""

import qdarktheme

from win_caffeine import const
from win_caffeine import qt
from win_caffeine import utils
from win_caffeine import screen_lock
from win_caffeine import main_window


def run(*args, **kwargs):
    """Run GUI app."""

    # Clear existing state
    screen_lock.release_screen_lock()

    # Enable HiDPI.
    qdarktheme.enable_hi_dpi()

    # Create the application
    app = qt.QApplication([])
    qdarktheme.setup_theme("auto", default_theme="light")

    mode = const.ON_OFF_MODE[screen_lock.is_on()]
    theme = utils.theme_from_palette(app.palette())
    icon_path = utils.get_icon_path(mode, theme)

    # Create the main window
    window = main_window.MainWindow(theme=theme)
    window.setWindowTitle(const.APP_NAME)
    window.setWindowIcon(qt.QIcon(icon_path))
    window.setFixedWidth(const.WINDOW_FIXED_WIDTH)
    window.setFixedHeight(const.WINDOW_FIXED_HEIGHT)

    # Create the system tray icon
    tray_icon = qt.QSystemTrayIcon(qt.QIcon(icon_path), parent=app)
    tray_icon.setToolTip(const.APP_NAME)

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
