import sys
from win_caffeine import qt


def main():
    # Create the application
    app = qt.QApplication([])

    # Create the main window (optional)
    window = qt.QMainWindow()  # Replace with your main window class or use None

    # Create the system tray icon
    tray_icon = qt.QSystemTrayIcon(qt.QIcon("assets/icon.png"), parent=app)
    tray_icon.setToolTip("App Name")

    # Create the system tray menu
    tray_menu = qt.QMenu()
    tray_menu.addAction("Restore", window.showNormal)  # Restore the main window
    tray_menu.addAction("Exit", app.quit)  # Quit the application
    tray_icon.setContextMenu(tray_menu)

    # Show the main window (optional)
    if window is not None:
        window.show()

    # Minimize to system tray
    tray_icon.show()
    app.setQuitOnLastWindowClosed(False)

    # Start the application event loop
    app.exec_()


if __name__ == '__main__':
    sys.exit(main())