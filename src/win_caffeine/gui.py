"""GUI app implementation."""
from win_caffeine import settings
from win_caffeine import qt
from win_caffeine import main_window


def run(*args, **kwargs):
    """Run GUI app."""

    settings.init()
    # Create the application
    app = qt.QApplication([])
    settings.set_theme("auto", app)

    # Create the main window
    window = main_window.MainWindow()

    # Create the system tray icon
    tray_icon = qt.QSystemTrayIcon(qt.QIcon(settings.icon_path.coffee_on), parent=app)
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
    
    # Start in prevent screen lock state
    window.on_toggle_button_clicked()
    app.setQuitOnLastWindowClosed(False)

    # Start the application event loop
    return app.exec_()
